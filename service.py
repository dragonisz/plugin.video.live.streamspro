# -*- coding: utf-8 -*-
import xbmcaddon, xbmc, xbmcgui
import sys, os
addon = xbmcaddon.Addon('plugin.video.livestreamspro')
sys.path.append(xbmc.translatePath(os.path.join(xbmc.translatePath(addon.getAddonInfo('Path')), 'lib')))

def download_epg():
    if addon.getSetting("epg_enable") == "true":
        epg_link = addon.getSetting("epg_link")
        try:
            if epg_link != "":
                epg_file = os.path.join(profile, "epg.xml")
                dp = xbmcgui.DialogProgressBG()
                dp.create("Live Streams Pro", "Downloading EPG")
                if os.path.exists(epg_file):
                    os.remove(epg_file)
                url = epg_link
                urllib.urlretrieve(url, epg_file, lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        except: 
            pass

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except: 
        percent = 100
        dp.update(percent)
        time.sleep(20)
        dp.close()
    if dp.iscanceled(): 
        dp.close()

if __name__ == "__main__":
    download_epg()