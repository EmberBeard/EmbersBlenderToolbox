import bpy

#===========================================================
# Global toolbox properties
#===========================================================

class ToolBoxProperties(bpy.types.PropertyGroup):
    # https://docs.blender.org/api/current/bpy_types_enum_items/property_subtype_items.html#rna-enum-property-subtype-items
    BlendShapesToApplyOnCommand: bpy.props.StringProperty(
        name="ShapeKeysToApply",
        description="A list of names and values. These relate to blend shapes and values",
        default="This is just some placeholder text",
        maxlen=1024,
        #subtype='BYTE_STRING'
    )
    
    AnimationMarkersFilePath: bpy.props.StringProperty(
        name="AnimationMarkersFilePath",
        description="Path to a txt file denoting animation marker names and spacing",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )

classes = (
    ToolBoxProperties,
)

#-----------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.EmbersToolBox = bpy.props.PointerProperty(type=ToolBoxProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)