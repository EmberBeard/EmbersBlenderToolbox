import bpy

from . import Operators_Armature, Operators_Mesh, Operators_Utility, Properties

bl_info = {
    "name": "Ember's Toolbox",
    "author": "Ember",
    "version": (0, 0, 6),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Ember's Toolbox",
    "description": "A set of utilities written by and for Ember Beard",
    "category": "Development",
}

#===========================================================
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

        TextFeild = self.layout.column(align=True)
        TextFeild.prop(context.scene.EmbersToolBox, "BlendShapesToApplyOnCommand", text="")
        ApplyShapeKeysRow = self.layout.row()
        ApplyShapeKeysRow.operator("mesh.apply_shape_key_values", text="Apply Shape Key Values to Mesh")
        
        self.layout.separator()
        
        self.layout.label(text="Rigging")
        BindControlRigRow = self.layout.row()
        BindControlRigRow.operator("armature.bind_control_rig", text="Bind control rig")
        RemoveControlRigRow = self.layout.row()
        RemoveControlRigRow.operator("armature.remove_control_rig", text="Remove control rig bindings")
        
        self.layout.separator()

        self.layout.label(text="Animation")
        InputFile = self.layout.column(align=True)
        InputFile.prop(context.scene.EmbersToolBox, "AnimationMarkersFilePath", text="")
        ImportAnimationMarkersRow = self.layout.row()
        ImportAnimationMarkersRow.operator("animation.import_animation_markers", text="import Animation Markers")
        
        self.layout.separator()
        
        self.layout.label(text="Development")
        ClearRow = self.layout.row()
        ClearRow.operator("console.custom_clear", text="Clear the terminal")

#===========================================================
# Boilerplate registration within Blender 3D
#===========================================================

classes = (
    VIEW3D_PT_EmbersTools,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    Operators_Armature.register()
    Operators_Mesh.register()
    Operators_Utility.register()
    Properties.register()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.EmbersToolBox
    Operators_Armature.unregister()
    Operators_Mesh.unregister()
    Operators_Utility.unregister()
    Properties.unregister()

if __name__ == "__main__":
    register()