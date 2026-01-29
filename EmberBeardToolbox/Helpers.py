import bpy

#-----------------------------------------------------------

def ShowMessageBox(title = "Example", message = "No message provided", icon = 'INFO'): #https://blender.stackexchange.com/questions/109711/how-to-popup-simple-message-box-from-python-console
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
#-----------------------------------------------------------
