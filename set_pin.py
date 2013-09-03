import xbmcgui
import resources.lib.utils as utils
from resources.lib.database import Database, DBSettings

#create the dialog
dialog = xbmcgui.Dialog()

database = Database()
database.connect()
database.checkDBStructure()

settings = DBSettings(database)

#check if there is a current pin
current_pin = settings.getPIN()
allow_change = True

if(current_pin != '0000'):
    allow_change = False

    #ask user to input current pin
    user_input = dialog.numeric(0,'Enter Current PIN')

    if(user_input == current_pin):
        allow_change = True
    else:
        dialog.ok('Error','Incorrect PIN')

#ask the user for a new pin
if(allow_change):
    first_try = dialog.numeric(0,'Enter new PIN')
    second_try = dialog.numeric(0,'Confirm new PIN')

    if(first_try == second_try):
        settings.setPIN(first_try)
        dialog.ok('Success','PIN Changed')
    else:
        #pins don't match
        dialog.ok('Error','PIN did not match')
