import bpy
import os

bl_info = {
    "name": "Ember's Toolbox",
    "author": "Ember",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Ember's Toolbox",
    "description": "A set of utilities written by and for Ember Beard",
    "category": "Development",
}

#===========================================================
# Mini utility functions
#===========================================================

def GetArmatureModifierFromObject(InObject):
    for modifier in InObject.modifiers:
        if (modifier.type == 'ARMATURE'):
            return modifier
    return None

#-----------------------------------------------------------

def DestroyShapeKeyByNameIfItExists(InObject, MarkerName):
    if MarkerName in InObject.data.shape_keys.key_blocks:
        index = InObject.data.shape_keys.key_blocks.keys().index(MarkerName)
        InObject.active_shape_key_index = index
        bpy.ops.object.shape_key_remove()

#-----------------------------------------------------------

def SaveCurrentFramePoseAsShapeKey(InObject, MarkerName, ModifierName):
    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=ModifierName)
    InObject.data.shape_keys.key_blocks[ModifierName].name = MarkerName #When you save a shapekey from a modifier it inherits the name of the modifier. If a shapekey with that name already exists then it's corrected. I do not presently account for this but at the same time - I WILL NEVER leave a shape key left with the default name, so in theory they shouldn't be a problem....... but this will be an issue for someone at some point, consider this your probably too late warning and subsequent appology. (hugs)

#===========================================================
# Custom operators
#===========================================================

# Shapekey recapture operator
#-----------------------------------------------------------

class MES_OT_RecaptureShapeKeys(bpy.types.Operator):
    bl_idname = "mesh.recapture_shape_keys"
    bl_label = "Recapture Anim Timeline Markers As Shape Keys"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Recapturing all timeline marked animation poses as shape keys")
        PrimaryObject = context.active_object
        Selection = context.selected_objects
        
        if(len(Selection) == 0): # we do this check first because clicking off a mesh WILL still result in an active object
            print("Empty selection")
            return {"CANCELLED"}
        if(PrimaryObject is None):
            print("No object selected")
            return {"CANCELLED"}
        if(PrimaryObject.type != 'MESH'):
            print("This operation only acts on meshes")
            return {"CANCELLED"}
        
        ArmatureModifier = GetArmatureModifierFromObject(PrimaryObject)
        if(ArmatureModifier is None):
            print("No Armature Modifier Found")
            return {"CANCELLED"}
        
        Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
        # ^ Timeline markers are UNSORTED BY DEFAULT. This puts them in order (lowest frame number to greatest)
        for M in Markers:
            print(M.frame, "=", M.name)
            context.scene.frame_set(M.frame)
            DestroyShapeKeyByNameIfItExists(PrimaryObject, M.name)
            SaveCurrentFramePoseAsShapeKey(PrimaryObject, M.name, ArmatureModifier.name)
        return {"FINISHED"}

# Bind Control Rig operator
#-----------------------------------------------------------

class ARM_OT_BindControlRig(bpy.types.Operator):
    bl_idname = "armature.bind_control_rig"
    bl_label = "Bind Control Rig"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Binding the control rig")
        return {"FINISHED"}

# Remove Control Rig operator
#-----------------------------------------------------------

class ARM_OT_RemoveControlRig(bpy.types.Operator):
    bl_idname = "armature.remove_control_rig"
    bl_label = "Remove The Control Rig"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Removing the control rig")
        Selection = context.selected_objects
        if(len(Selection) != 1):
            print("Must have only one armature object selected")
            return {"CANCELLED"}
        if(context.active_object.type != 'ARMATURE'):
            print("Must have only one armature object selected")
            return {"CANCELLED"}
        
        armature = context.active_object
        current_mode = context.mode
        bpy.ops.object.mode_set(mode='POSE')
        for bone in armature.pose.bones:
            # Check if the bone has a "COPY_TRANSFORMS" constraint
                for constraint in bone.constraints:
                    if constraint.type == 'COPY_TRANSFORMS':
                        # Remove the constraint
                        bone.constraints.remove(constraint)
        bpy.ops.object.mode_set(mode=current_mode)
        print()
        return {"FINISHED"}

# Clear Console operator
#-----------------------------------------------------------

class CON_OT_ClearConsole(bpy.types.Operator):
    bl_idname = "console.custom_clear"
    bl_label = "Custom Console Clear"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        if(os.name == "nt"):
            os.system("cls")
        else:
            os.system('clear')
        
        return {"FINISHED"}

#============================pip install fake-bpy-module-latest===============================
# The main helper panel with all the UI
#===========================================================

class VIEW3D_PT_EmbersTools(bpy.types.Panel):
    bl_space_type = "VIEW_3D" # https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items
    bl_region_type = "UI" # https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items
    bl_category = "Ember's Tools"
    bl_label = "Ember'sToolbox"
    
    def draw(self, context):
        
        self.layout.label(text="Geometry")
        RecaptureRow = self.layout.row()
        RecaptureRow.operator("mesh.recapture_shape_keys", text="Recapture as Shape Keys")
        
        self.layout.separator()
        
        self.layout.label(text="Rigging")
        BindControlRigRow = self.layout.row()
        BindControlRigRow.operator("armature.bind_control_rig", text="Bind control rig")
        BindControlRigRow = self.layout.row()
        BindControlRigRow.operator("armature.remove_control_rig", text="Remove control rig bindings")
        
        self.layout.separator()
        
        self.layout.label(text="Development")
        ClearRow = self.layout.row()
        ClearRow.operator("console.custom_clear", text="Clear the terminal")

#===========================================================
# Boilerplate registration within Blender 3D
#===========================================================

def register():
    bpy.utils.register_class(VIEW3D_PT_EmbersTools)
    bpy.utils.register_class(MES_OT_RecaptureShapeKeys)
    bpy.utils.register_class(ARM_OT_BindControlRig)
    bpy.utils.register_class(ARM_OT_RemoveControlRig)
    bpy.utils.register_class(CON_OT_ClearConsole)

def unregister():
    bpy.utils.unregister_class(CON_OT_ClearConsole)
    bpy.utils.unregister_class(ARM_OT_RemoveControlRig)
    bpy.utils.unregister_class(ARM_OT_BindControlRig)
    bpy.utils.unregister_class(MES_OT_RecaptureShapeKeys)
    bpy.utils.unregister_class(VIEW3D_PT_EmbersTools)

if __name__ == "__main__":
    register()