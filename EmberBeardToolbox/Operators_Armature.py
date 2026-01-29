import bpy

from . import Helpers

#===========================================================
# ARMATURE OPERATORS
#===========================================================

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

#-----------------------------------------------------------

classes = (
    ARM_OT_BindControlRig,
    ARM_OT_RemoveControlRig,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)