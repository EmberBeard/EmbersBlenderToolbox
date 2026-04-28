import bpy

class MESH_OT_remove_df_groups(bpy.types.Operator):
    #DF = Deletable Forming
    """Remove all vertex groups starting with 'DF_' from the active object"""
    bl_idname = "mesh.remove_df_groups"
    bl_label = "Remove DF_ Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enable if an object is selected and it is a mesh
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        
        # Find all groups starting with the prefix
        to_remove = [vg for vg in obj.vertex_groups if vg.name.startswith("DF_")]
        
        if not to_remove:
            self.report({'INFO'}, "No vertex groups found with prefix 'DF_'")
            return {'CANCELLED'}

        count = len(to_remove)
        for vg in to_remove:
            obj.vertex_groups.remove(vg)
            
        self.report({'INFO'}, f"Successfully removed {count} 'DF_' groups")
        return {'FINISHED'}

#-----------------------------------------------------------

def ShowMessageBox(title = "Example", message = "No message provided", icon = 'INFO'): #https://blender.stackexchange.com/questions/109711/how-to-popup-simple-message-box-from-python-console
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

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
            bpy.ops.object,modifier_apply_as_shapekey(keep_modifier=True, modifier=AM.name)
        for AM in ArmatureModifiers:
            InObject.data.shape_keys.key_blocks[AM.name].value = 1.0
        InObject.shape_key_add(name=MarkerName, from_mix=True)
        for AM in ArmatureModifiers:
            InOjbect.active_shape_key_index = InObject.data.shape_keys.key_blocks.keys().index(AM.name)
            bpy.ops.object.shape_key_remove()

#-----------------------------------------------------------
    
class MES_OT_RecaptureShapeKeys(bpy.types.Operator):
    bl_idname = "mesh.recapture_shape_keys"
    bl_label = "Recapture Anim Timeline Markers As Shape Keys"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        # Only enable if an object is selected and it is a mesh
        return context.active_object is not None and context.active_object.type == 'MESH' and len(GetArmatureModifiersFromObject(context.active_object)) > 0
    
    def execute(self, context):
        print("Recapturing all timeline marked animation poses as shape keys")
        PrimaryObject = context.active_object
        Selection = context.selected_objects
        
        if(len(Selection) == 0): # we do this check first because clicking off a mesh WILL still result in an active object
            ShowMessageBox("Failed", "There is no selection", 'ERROR')
            print("Empty selection")
            return {"CANCELLED"}
        if(PrimaryObject is None):
            ShowMessageBox("Failed", "No object selected", 'ERROR')
            return {"CANCELLED"}
        if(PrimaryObject.type != 'MESH'):
            ShowMessageBox("Failed", "You must have a mesh object focused as you active object", 'ERROR')
            return {"CANCELLED"}
        
        ArmatureModifiers = GetArmatureModifiersFromObject(PrimaryObject)
        if(ArmatureModifiers is None):
            ShowMessageBox("Failed", "The mesh has no Armature modifier", 'ERROR')
            return {"CANCELLED"}
        
        Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
        # ^ Timeline markers are UNSORTED BY DEFAULT. This puts them in order (lowest frame number to greatest)
        
        if len(Markers) == 0:
            ShowMessageBox("Skipping", "There are no animation markers in the timeline to sample", 'WARNING')
            return {"CANCELLED"}
        
        CreateBasisShapekeyIfNoneExist(PrimaryObject)
        ClearAllShapekeys(PrimaryObject)
        
        for M in Markers:
            print(M.frame, "=", M.name)
            context.scene.frame_set(M.frame)
            clean_name = M.name.strip()
            DestroyShapeKeyByNameIfItExists(PrimaryObject, clean_name)
            SaveCurrentFramePoseAsShapeKey(PrimaryObject, clean_name, ArmatureModifiers)
        return {"FINISHED"}

class VIEW3D_PT_df_cleanup_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport 'Tool' tab"""
    bl_label = "Vertex Group Tools"
    bl_idname = "VIEW3D_PT_df_cleanup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Experimental'  # This places it in the 'Tool' tab of the N-panel

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("mesh.remove_df_groups", icon='X', text="Clean 'DF_' Groups")
        col2 = layout.column(align=True)
        col2.operator("mesh.recapture_shape_keys", text="recapture shape keys")

classes = (
    VIEW3D_PT_df_cleanup_panel,
    MESH_OT_remove_df_groups,
    MES_OT_RecaptureShapeKeys,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()