import xbmc
import resources.lib.utils as utils

class HistoryService:
    monitor = None
    
    def __init__(self):
        utils.log("Starting History Service")
        self.monitor = HistoryPlayerMonitor(on_play_started = self.playStarted)

    def run(self):
        while(not xbmc.abortRequested):
            xbmc.sleep(500)

    def playStarted(self):
        
        if(self.monitor.isPlayingVideo()):
            utils.log(self.monitor.getPlayingFile())

class HistoryPlayerMonitor(xbmc.Player):
    onPlay = None
    
    def __init__(self,*args,**kwargs):
        xbmc.Player.__init__(self)

        self.onPlay = kwargs['on_play_started']
        
    def onPlayBackStarted(self):
        self.onPlay()


historyService = HistoryService()
historyService.run()
