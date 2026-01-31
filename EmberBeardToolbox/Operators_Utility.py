import bpy
import os

from . import Properties, Helpers

#===========================================================
# Utility Operators
#===========================================================

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

#-----------------------------------------------------------

classes = (
    CON_OT_ClearConsole,
)

#-----------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)