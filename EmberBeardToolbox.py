import bpy
import os

bl_info = {
    "name": "Ember's Toolbox",
    "author": "Ember",
    "version": (0, 0, 4),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > Ember's Toolbox",
    "description": "A set of utilities written by and for Ember Beard",
    "category": "Development",
}

#===========================================================
# Mini utility functions
#===========================================================

def ShowMessageBox(title = "Example", message = "No message provided", icon = 'INFO'): #https://blender.stackexchange.com/questions/109711/how-to-popup-simple-message-box-from-python-console
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

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
            ShowMessageBox("Failed", "There is no selection", 'ERROR')
            print("Empty selection")
            return {"CANCELLED"}
        if(PrimaryObject is None):
            ShowMessageBox("Failed", "No object selected", 'ERROR')
            return {"CANCELLED"}
        if(PrimaryObject.type != 'MESH'):
            ShowMessageBox("Failed", "You must have a mesh object focused as you active object", 'ERROR')
            return {"CANCELLED"}
        
        ArmatureModifier = GetArmatureModifierFromObject(PrimaryObject)
        if(ArmatureModifier is None):
            ShowMessageBox("Failed", "The mesh has no Armature modifier", 'ERROR')
            return {"CANCELLED"}
        
        Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
        # ^ Timeline markers are UNSORTED BY DEFAULT. This puts them in order (lowest frame number to greatest)
        for M in Markers:
            print(M.frame, "=", M.name)
            context.scene.frame_set(M.frame)
            clean_name = M.name.strip()
            DestroyShapeKeyByNameIfItExists(PrimaryObject, clean_name)
            SaveCurrentFramePoseAsShapeKey(PrimaryObject, clean_name, ArmatureModifier.name)
        return {"FINISHED"}

# Bind Control Rig operator
#-----------------------------------------------------------

class ARM_OT_BindControlRig(bpy.types.Operator):
    bl_idname = "armature.bind_control_rig"
    bl_label = "Bind Control Rig"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Binding the control rig")
        Selection = context.selected_objects
        if(len(Selection) != 2):
            print("Must have only two armature objects selected")
            return {"CANCELLED"}
        if(context.selected_objects[0].type != 'ARMATURE' or context.selected_objects[1].type != 'ARMATURE'):
            print("Must have only two armature objects selected")
            return {"CANCELLED"}
        
        armature_from = None
        armature_to = None

        if(context.active_object == context.selected_objects[0]):
            armature_to = context.selected_objects[0]
            armature_from = context.selected_objects[1]
        else:
            armature_from = context.selected_objects[0]
            armature_to = context.selected_objects[1]
        
        current_mode = context.mode
        bpy.ops.object.mode_set(mode='POSE')

        copy_transform_constraint = armature_to.constraints.new('COPY_TRANSFORMS')
        copy_transform_constraint.target = armature_from
        copy_transform_constraint.target_space = 'WORLD'
        copy_transform_constraint.owner_space = 'WORLD'

        for t_bone in armature_to.pose.bones:
            for f_bone in armature_from.pose.bones:
                if (t_bone.name == f_bone.name):
                    copy_con = t_bone.constraints.new('COPY_TRANSFORMS')
                    copy_con.target = armature_from
                    copy_con.subtarget = f_bone.name
                    copy_con.target_space = 'WORLD' # consider POSE
                    copy_con.owner_space = 'WORLD' # consider POSE
                    break

        bpy.ops.object.mode_set(mode=current_mode)

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
        if(len(Selection) == 0):
            print("Must have one armature object as the active selection")
            return {"CANCELLED"}
        if(context.active_object.type != 'ARMATURE'):
            print("Must have one armature object as the active selection")
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

# Import Animation Markers
#-----------------------------------------------------------

class ToolBoxProperties(bpy.types.PropertyGroup):
    AnimationMarkersFilePath: bpy.props.StringProperty(
        name="AnimationMarkersFilePath",
        description="Path to a txt file denoting animation marker names and spacing",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )

class ANIM_OT_ImportAnimationMarkers(bpy.types.Operator):
    bl_idname = "animation.import_animation_markers"
    bl_label = "ImportAnimationMarkers"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        
        marker_path = context.scene.EmbersToolBox.AnimationMarkersFilePath
        with open(marker_path, 'r') as open_file:
            ShowMessageBox("Success", "Importing " + marker_path, 'INFO')
        
            Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
            for M in Markers:
                context.scene.timeline_markers.remove(M)
        
            line_count = 0
            for line in open_file:
                if len(line) > 1:
                    final_string = line.strip() # this apparently is a cleanup function that will just remove preceeding and trailing newline characters - neat :3
                    if len(final_string) > 1:
                        context.scene.timeline_markers.new(final_string, frame=line_count)
                line_count = line_count + 1
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
    ToolBoxProperties,
    VIEW3D_PT_EmbersTools,
    MES_OT_RecaptureShapeKeys,
    ARM_OT_BindControlRig,
    ARM_OT_RemoveControlRig,
    ANIM_OT_ImportAnimationMarkers,
    CON_OT_ClearConsole,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.EmbersToolBox = bpy.props.PointerProperty(type=ToolBoxProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.EmbersToolBox

if __name__ == "__main__":
    register()