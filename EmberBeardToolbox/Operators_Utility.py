import bpy
import os

from . import Properties, Helpers

#===========================================================
# Global toolbox properties
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
            ShowMessageBox("Success", "Importing " + marker_path, 'INFO')
        
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

classes = (
    ANIM_OT_ImportAnimationMarkers,
    CON_OT_ClearConsole,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)