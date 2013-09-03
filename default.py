import xbmc,xbmcvfs,xbmcgui
import time
import resources.lib.utils as utils
from resources.lib.database import Database, WatchHistory,DBSettings

class HistoryService:
    playerMonitor = None
    updateMonitor = None
    historyDB = None
    settings = None
    require_pin = False  #need to store this as it might change
    
    def __init__(self):
        utils.log("Starting History Service")
        self.playerMonitor = HistoryPlayerMonitor(on_play_started = self.playStarted)
        self.updateMonitor = HistorySettingsMonitor(update_settings = self.onSettingsUpdate)
        
        #setup the database connection
        database = Database()
        database.connect()
        database.checkDBStructure()

        self.historyDB = WatchHistory(database)
        self.settings = DBSettings(database)

        if(utils.getSetting('require_pin_on_change') == 'true'):
            self.require_pin = True

        #backup the settings file
        self._settingsBackup()

    def run(self):
        while(not xbmc.abortRequested):
            xbmc.sleep(500)

    def playStarted(self):
        
        if(self.playerMonitor.isPlayingVideo() and utils.getSetting('monitor_video') == 'true'):
            videoTag = self.playerMonitor.getVideoInfoTag()

            utils.log("Logging: " + videoTag.getTitle(),xbmc.LOGDEBUG)
            self.historyDB.insert(("video",videoTag.getTitle(),self.playerMonitor.getPlayingFile(),int(time.time())))
            
        elif(self.playerMonitor.isPlayingAudio() and utils.getSetting('monitor_music') == 'true'):
            audioTag = self.playerMonitor.getMusicInfoTag()

            utils.log("Logging: " + audioTag.getTitle(),xbmc.LOGDEBUG)
            self.historyDB.insert(('audio',audioTag.getTitle(),self.playerMonitor.getPlayingFile(),int(time.time())))

    def onSettingsUpdate(self):
        #check if a pin is required to change settings
        if(self.require_pin):
            dialog = xbmcgui.Dialog()
            
            current_pin = self.settings.getPIN()
            
            #ask the user for their pin
            user_try = dialog.numeric(0,'Pin required to change settings')

            if(current_pin == user_try):
                #make backup of new settings
                self._settingsBackup()
                
                if(utils.getSetting('require_pin_on_change') == 'false'):
                    self.require_pin = False
            else:
                #restore the settings file
                self._settingsRestore()
                dialog.ok('Error','Incorrect PIN')
        else:
            #check this setting in case it's the one that changed
            if(utils.getSetting('require_pin_on_change') == 'true'):
                    self.require_pin = True

    def _settingsBackup(self):
        #make a backup of the settings file (in case pin is incorrect)
        settings_file = xbmc.translatePath(utils.data_dir() + "settings.xml")

        if(xbmcvfs.exists(settings_file)):
            xbmcvfs.copy(settings_file,settings_file + ".bak")

    def _settingsRestore(self):
        #restore the settings file (in case pin is incorrect)
        settings_file = xbmc.translatePath(utils.data_dir() + "settings.xml")

        if(xbmcvfs.exists(settings_file)):
            xbmcvfs.copy(settings_file + ".bak",settings_file)

class HistoryPlayerMonitor(xbmc.Player):
    onPlay = None
    
    def __init__(self,*args,**kwargs):
        xbmc.Player.__init__(self)

        self.onPlay = kwargs['on_play_started']
        
    def onPlayBackStarted(self):
        self.onPlay()

class HistorySettingsMonitor(xbmc.Monitor):
    update_settings = None
    
    def __init__(self,*args,**kwargs):
        xbmc.Monitor.__init__(self)
        self.update_settings = kwargs['update_settings']

    def onSettingsChanged(self):
        self.update_settings()

historyService = HistoryService()
historyService.run()
