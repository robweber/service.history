import xbmc
import time
import resources.lib.utils as utils
from resources.lib.database import Database, WatchHistory

class HistoryService:
    monitor = None
    historyDB = None
    
    def __init__(self):
        utils.log("Starting History Service")
        self.monitor = HistoryPlayerMonitor(on_play_started = self.playStarted)

        #setup the database connection
        database = Database()
        database.connect()
        database.checkDBStructure()

        self.historyDB = WatchHistory(database)

    def run(self):
        while(not xbmc.abortRequested):
            xbmc.sleep(500)

    def playStarted(self):
        
        if(self.monitor.isPlayingVideo()):
            videoTag = self.monitor.getVideoInfoTag()

            utils.log("Logging: " + videoTag.getTitle(),xbmc.LOGDEBUG)
            self.historyDB.insert(("video",videoTag.getTitle(),int(time.time())))

class HistoryPlayerMonitor(xbmc.Player):
    onPlay = None
    
    def __init__(self,*args,**kwargs):
        xbmc.Player.__init__(self)

        self.onPlay = kwargs['on_play_started']
        
    def onPlayBackStarted(self):
        self.onPlay()


historyService = HistoryService()
historyService.run()
