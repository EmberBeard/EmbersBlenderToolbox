import bpy

from . import Properties, Helpers

#===========================================================
# Mini utility functions
#===========================================================

#-----------------------------------------------------------
    
def GetArmatureModifiersFromObject(InObject):
    modifiers = [mod for mod in InObject.modifiers if mod.type == 'ARMATURE']
    if(len(modifiers) == 0):
        return None
    return modifiers

#-----------------------------------------------------------

def DestroyShapeKeyByNameIfItExists(InObject, MarkerName):
    if MarkerName in InObject.data.shape_keys.key_blocks:
        index = InObject.data.shape_keys.key_blocks.keys().index(MarkerName)
        InObject.active_shape_key_index = index
        bpy.ops.object.shape_key_remove()

#-----------------------------------------------------------

def CreateBasisShapekeyIfNoneExist(InObject):
    # Check if the object has shape key data at all
    if not InObject.data.shape_keys or not InObject.data.shape_keys.key_blocks:
        # Create the first shape key, which Blender automatically treats as the "Basis"
        InObject.shape_key_add(name="Basis", from_mix=False)

#-----------------------------------------------------------

def ClearAllShapekeys(InObject):
    print("Clear has been called")
    if InObject.data.shape_keys:
        for shapeKey in InObject.data.shape_keys.key_blocks:
            shapeKey.value = 0.0
    
#-----------------------------------------------------------

def SaveCurrentFramePoseAsShapeKey(InObject, MarkerName, ArmatureModifiers):
    if (len(ArmatureModifiers) <= 0):
        return
    elif (len(ArmatureModifiers) == 1):
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=ArmatureModifiers[0].name)
        InObject.data.shape_keys.key_blocks[ArmatureModifiers[0].name].name = MarkerName #When you save a shapekey from a modifier it inherits the name of the modifier. If a shapekey with that name already exists then it's corrected. I do not presently account for this but at the same time - I WILL NEVER leave a shape key left with the default name, so in theory they shouldn't be a problem....... but this will be an issue for someone at some point, consider this your probably too late warning and subsequent appology. (hugs)
    else:
        for AM in ArmatureModifiers:
            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=AM.name)
        for AM in ArmatureModifiers:
            InObject.data.shape_keys.key_blocks[AM.name].value = 1.0
        InObject.shape_key_add(name=MarkerName, from_mix=True)
        for AM in ArmatureModifiers:
            InObject.active_shape_key_index = InObject.data.shape_keys.key_blocks.keys().index(AM.name)
            bpy.ops.object.shape_key_remove()

#-----------------------------------------------------------

def parse_name_number_string(data_string):
    # Split by comma and clean up surrounding whitespace
    parts = [item.strip() for item in data_string.split(',')]
    
    # Pair items (0,1), (2,3), etc. using an iterator
    it = iter(parts)
    return {name: float(num) for name, num in zip(it, it)}

#===========================================================
# MESH OPERATORS
#===========================================================

# Shapekey recapture operator
#-----------------------------------------------------------

class MES_OT_RecaptureShapeKeys(bpy.types.Operator):
    bl_idname = "mesh.recapture_shape_keys"
    bl_label = "Recapture Anim Timeline Markers As Shape Keys"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        # Only enable if an object is selected and it is a mesh with no Armature Modifier
        return context.active_object is not None and context.active_object.type == 'MESH' and len(GetArmatureModifiersFromObject(context.active_object)) > 0
    
    def execute(self, context):
        print("Recapturing all timeline marked animation poses as shape keys")
        PrimaryObject = context.active_object
        Selection = context.selected_objects
        
        if(len(Selection) == 0): # we do this check first because clicking off a mesh WILL still result in an active object
            Helpers.ShowMessageBox("Failed", "There is no selection", 'ERROR')
            print("Empty selection")
            return {"CANCELLED"}
        if(PrimaryObject is None):
            Helpers.ShowMessageBox("Failed", "No object selected", 'ERROR')
            return {"CANCELLED"}
        if(PrimaryObject.type != 'MESH'):
            Helpers.ShowMessageBox("Failed", "You must have a mesh object focused as you active object", 'ERROR')
            return {"CANCELLED"}
        
        ArmatureModifiers = GetArmatureModifiersFromObject(PrimaryObject)
        if(ArmatureModifiers is None):
            Helpers.ShowMessageBox("Failed", "The mesh has no Armature modifier", 'ERROR')
            return {"CANCELLED"}
        
        Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
        # ^ Timeline markers are UNSORTED BY DEFAULT. This puts them in order (lowest frame number to greatest)
        
        if len(Markers) == 0:
            Helpers.ShowMessageBox("Skipping", "There are no animation markers in the timeline to sample", 'WARNING')
            return {"CANCELLED"}
        
        CreateBasisShapekeyIfNoneExist(PrimaryObject)
        ClearAllShapekeys(PrimaryObject)
        
        for M in Markers:
            print(M.frame, "=", M.name)
            if len(M.name) <= 0:
                continue
            if M.name.startswith('#'): # If the string starts with a # then it's a comment and not something we want to catpure
                continue
            context.scene.frame_set(M.frame)
            clean_name = M.name.strip()
            DestroyShapeKeyByNameIfItExists(PrimaryObject, clean_name)
            SaveCurrentFramePoseAsShapeKey(PrimaryObject, clean_name, ArmatureModifiers)
            ClearAllShapekeys(PrimaryObject)
        return {"FINISHED"}

# Apply shapekey values to mesh
#-----------------------------------------------------------

class MES_OT_ApplyShapeKeyValues(bpy.types.Operator):
    bl_idname = "mesh.apply_shape_key_values"
    bl_label = "Apply the list of provided shapekeys and values to the selected mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # Only enable if an object is selected and it is a mesh with no Armature Modifier
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        print("Applying given shapekey values to the selected mesh")
        print(context.scene.EmbersToolBox.BlendShapesToApplyOnCommand)
        
        # Example Usage:
        #This custom function expects strings formatted like this: "john smith 7.672 jane doe 5.0 bill 10 "
        NameNumberMap = parse_name_number_string(context.scene.EmbersToolBox.BlendShapesToApplyOnCommand)
        
        # Now to loop over the meshes selected and set the blendshapes
        # 1. Loop through all currently selected objects
        for obj in bpy.context.selected_objects:
            # 2. Safety check: Ensure the object is a mesh and has shape keys
            if obj.type == 'MESH' and obj.data.shape_keys:
                
                # Access the collection of shape keys (key_blocks)
                key_blocks = obj.data.shape_keys.key_blocks
                
                # 3. Iterate through your name-number map
                for name, value in NameNumberMap.items():
                
                    # 4. Check if a shape key with that name exists on THIS mesh
                    if name in key_blocks:
                        # Set the blendshape value
                        key_blocks[name].value = value
                        print(f"Set '{name}' to {value} on {obj.name}")
        return {"FINISHED"}

# Copy shape key values as a string
#-----------------------------------------------------------

class Mes_OT_CopyShapeKeyValues(bpy.types.Operator):
    bl_idname = "mesh.copy_shape_key_values_as_string"
    bl_label = "Copies all the shapekeys to the clipboard in a format where they can be easily reapplied"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH' or not obj.data.shape_keys:
            Helpers.ShowMessageBox("Error: No mesh with shape keys selected.")
            return
        
        active_shapes = []
    
        # Iterate and filter values > 0
        for key in obj.data.shape_keys.key_blocks:
            if key.value > 0:
                active_shapes.append(f"{key.name}, {key.value:.3f}, ")
    
        if active_shapes:
            final_string = "".join(active_shapes)
            # 1. Store in Blender's window manager clipboard
            bpy.context.window_manager.clipboard = final_string
            Helpers.ShowMessageBox(f"Copied to clipboard: {final_string}")
        else:
            Helpers.ShowMessageBox("No active shape keys found to copy.")
        
        return {"FINISHED"}

#-----------------------------------------------------------

classes = (
    MES_OT_RecaptureShapeKeys,
    MES_OT_ApplyShapeKeyValues,
    Mes_OT_CopyShapeKeyValues,
)

#-----------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)