# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, time


class MyXBMCPlayer(xbmc.Player):
    global addon 
    addon = xbmcaddon.Addon('plugin.video.live.streamspro')

    def __init__( self, *args, **kwargs ):
        self.is_active = True
        self.urlplayed = False
        self.pdialogue=None
        self.url = None
        self.force_reload = addon.getSetting('force_reload')
        print "# XBMC Custom Player#"
    
    def play(self, url, listitem=None):
        print 'Now im playing... %s' % url
        self.is_active = True
        self.urlplayed = False
        start_time_play=time.time()
        if listitem is not None:
            xbmc.Player().play(url, listitem)
        else:
            xbmc.Player().play(url)

    def onNotification(self, sender, method, data):
        if method == 'Player.OnPlayBackStopped':
            if self.force_reload != "false":
                xbmc.Player().play(self.url)
        if method == 'Player.OnStop':
            if self.force_reload != "false":
                xbmc.Player().play(self.url)
        if method == 'Player.OnPlayBackStopped':
            if self.force_reload != "false":
                xbmc.Player().play(self.url)

	#def setdialogue( self, pdialogue ):
	#	self.pdialogue=pdialogue
		
    def onPlayBackStarted( self ):
        print "#Playback Started#"
        try:
            print "#Im playing :: " 
        except:
            print "#I failed get what Im playing#"
        if (self.pdialogue):
            self.pdialogue.close()
        self.urlplayed = True
            
    def onPlayBackEnded( self ):
        print "# Playback Ended #"
        if self.force_reload != "false":
            self.is_active = True
            xbmc.Player().play(self.url)
        else:
            self.is_active = False
        return True
        
    def onPlayBackStopped( self ):
        print "## Playback Stopped ##"
        if self.force_reload != "false":
            self.is_active = True
            xbmc.Player().play(self.url)
        else:
            self.is_active = False
        return True

