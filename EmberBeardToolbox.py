import bpy

bl_info = {
    "name": "Ember's Toolbox",
    "author": "Ember",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Ember's Toolbox",
    "description": "A set of utilities written by and for Ember Beard",
    "category": "Development",
}

def GetArmatureModifierFromObject(InObject):
    for modifier in InObject.modifiers:
        if (modifier.type == 'ARMATURE'):
            return modifier
    return None

def DestroyShapeKeyByNameIfItExists(InObject, MarkerName):
    if MarkerName in InObject.data.shape_keys.key_blocks:
        index = InObject.data.shape_keys.key_blocks.keys().index(MarkerName)
        InObject.active_shape_key_index = index
        bpy.ops.object.shape_key_remove()
    

def SaveCurrentFramePoseAsShapeKey(InObject, MarkerName, ModifierName):
    bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=ModifierName)
    InObject.data.shape_keys.key_blocks[ModifierName].name = MarkerName #When you save a shapekey from a modifier it inherits the name of the modifier. If a shapekey with that name already exists then it's corrected. I do not presently account for this but at the same time - I WILL NEVER leave a shape key left with the default name, so in theory they shouldn't be a problem....... but this will be an issue for someone at some point, consider this your probably too late warning and subsequent appology. (hugs)
    

class MES_OT_RecaptureShapeKeys(bpy.types.Operator):
    bl_idname = "mesh.recapture_shape_keys"
    bl_label = "Recapture Anim Timeline Markers As Shape Keys"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("custom job start")
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

class VIEW3D_PT_EmbersTools(bpy.types.Panel):
    bl_space_type = "VIEW_3D" # https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items
    bl_region_type = "UI" # https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items
    bl_category = "Ember"
    bl_label = "Ember'sToolbox"
    
    def draw(self, context):
        #define the UI layout of the pannel
        row1 = self.layout.row()
        row1.operator("mesh.primitive_cube_add", text="Make Cube")#bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        row2 = self.layout.row()
        row2.operator("mesh.primitive_ico_sphere_add", text="Make Ico Sphere")
        row3 = self.layout.row()
        row3.operator("object.shade_smooth", text="Make It Pretty")
        row4 = self.layout.row()
        row4.operator("object.delete", text="Nuke that MF")
        self.layout.separator()
        row5 = self.layout.row()
        row5.operator("mesh.recapture_shape_keys", text="Recapture as Shape Keys")
    
def register():
    bpy.utils.register_class(VIEW3D_PT_EmbersTools)
    bpy.utils.register_class(MES_OT_RecaptureShapeKeys)

def unregister():
    bpy.utils.unregister_class(MES_OT_RecaptureShapeKeys)
    bpy.utils.unregister_class(VIEW3D_PT_EmbersTools)

if __name__ == "__main__":
    register()