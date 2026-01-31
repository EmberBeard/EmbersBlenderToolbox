import bpy

from . import Helpers

#===========================================================
# Animation Operators
#===========================================================

# Import Animation Markers
#-----------------------------------------------------------

class ANIM_OT_ImportAnimationMarkers(bpy.types.Operator):
    bl_idname = "animation.import_animation_markers"
    bl_label = "ImportAnimationMarkers"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        marker_path = context.scene.EmbersToolBox.AnimationMarkersFilePath
        with open(marker_path, 'r') as open_file:
            Helpers.ShowMessageBox("Success", "Importing " + marker_path, 'INFO')
        
            Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
            for M in Markers:
                context.scene.timeline_markers.remove(M)
        
            line_count = 0
            for line in open_file:
                final_string = line.strip() # Strip removes preceding and trailing newline characters
                if len(final_string) > 0:
                    context.scene.timeline_markers.new(final_string, frame=line_count)
                line_count = line_count + 1
        return {"FINISHED"}

#-----------------------------------------------------------

class ANIM_OT_AnimateBlenShapesToMarkers(bpy.types.Operator):
    bl_idname = "animation.animate_blendshapes_to_timeline_markers"
    bl_label = "AnimateBlendShapeToTimelineMarkers"
    bl_options = {"REGISTER", "UNDO"}

    def KeyFrameAnimateShapeKey(context, ShapeKey, Value, FrameNumber):
        context.scene.frame_set(FrameNumber)
        ShapeKey.value = Value
        ShapeKey.keyframe_insert(data_path="value", frame=FrameNumber)
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH' or not obj.data.shape_keys:
            Helpers.ShowMessageBox("Error: No mesh with shape keys selected.")
            return

        Markers = sorted(context.scene.timeline_markers, key=lambda m: m.frame)
        for M in Markers:
            MarkerName = M.name.strip()
            if MarkerName in obj.data.shape_keys.key_blocks:
                ShapeKey = obj.data.shape_keys.key_blocks[MarkerName]
                CurrentFrame = M.frame
                ANIM_OT_AnimateBlenShapesToMarkers.KeyFrameAnimateShapeKey(context, ShapeKey, 0, CurrentFrame - 1)
                ANIM_OT_AnimateBlenShapesToMarkers.KeyFrameAnimateShapeKey(context, ShapeKey, 1, CurrentFrame)
                ANIM_OT_AnimateBlenShapesToMarkers.KeyFrameAnimateShapeKey(context, ShapeKey, 0, CurrentFrame + 1)

        return {"FINISHED"}

#-----------------------------------------------------------

classes = (
    ANIM_OT_ImportAnimationMarkers,
    ANIM_OT_AnimateBlenShapesToMarkers,
)

#-----------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)