import xbmcgui,xbmcplugin
import sys
import urlparse
import datetime
import resources.lib.utils as utils
from resources.lib.database import Database, WatchHistory, DBSettings


class HistoryGUI:
    params = None
    historyDB = None
    settings = None
    
    def __init__(self,params):
        self.params = params

        database = Database()
        database.connect()
        database.checkDBStructure()

        self.historyDB = WatchHistory(database)
        self.settings = DBSettings(database)

    def run(self):
        action = int(params['action'])

        utils.log("action " + str(action))
        if(action == 0):
            self._showHistory()
        elif(action == 1001):
            self._delete(params['id'])

    def _showHistory(self):
        #we are listing files
        xbmcplugin.setContent(int(sys.argv[1]),'files')
        xbmcplugin.setPluginCategory(int(sys.argv[1]),'Play History')
        context_url = "%s?%s"
        
        #load the history
        history = self.historyDB.getAllOrderedLimit('date',0,30)

        if(len(history) > 0):
            for entry in history:
                entryName = str(entry[2])

                #if the name is blank use the file path
                if(entryName == ''):
                    entryName = str(entry[3])
                    
                item = xbmcgui.ListItem(entryName,str(entry[4]),path=str(entry[3]))
                item.setProperty('IsPlayable','true')
                item.addContextMenuItems([('Delete from History','Xbmc.RunPlugin(%s?%s)' % (str(sys.argv[0]),'action=1001&id=' + str(entry[0])))])
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url= "%s" % (entry[3],),listitem=item,isFolder=False)
                
        else:
            item = xbmcgui.ListItem("No Items In History")
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"action=0"),listitem=item,isFolder=False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)
        
    def _delete(self,id):
        #check if we need PIN confirmation to do this
        if(utils.getSetting('require_pin_on_delete') == 'true'):
            user_try = xbmcgui.Dialog().numeric(0,'PIN Required')

            if(user_try == self.settings.getPIN()):
                self.historyDB.delete(id)
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().ok('Error','Incorrect PIN')
        else:
            self.historyDB.delete(id)
            xbmc.executebuiltin('Container.Refresh')
        
def get_params():
    param = {}
    try:
        for i in sys.argv:
            args = i
            if(args.startswith('?')):
                args = args[1:]
            param.update(dict(urlparse.parse_qsl(args)))
    except:
        pass
    return param

params = get_params()

#set an action if one does not exist
try:
    action = int(params['action'])
except:
    params['action'] = 0
    pass

gui = HistoryGUI(params)
gui.run()
