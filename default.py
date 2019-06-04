# -*- coding: utf-8 -*-
import urllib, re, os, sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
import cookielib, traceback, base64, time

addon = xbmcaddon.Addon('plugin.video.live.streamspro')
sys.path.append(xbmc.translatePath(os.path.join(xbmc.translatePath(addon.getAddonInfo('Path')), 'lib')))

from lib import _core 
from lib import slproxy 
from lib import updater
try: from xml.sax.saxutils import escape
except: traceback.print_exc()

try: import json
except: import simplejson as json

tsdownloader=False
hlsretry=False
viewmode=None

global gLSProDynamicCodeNumber
gLSProDynamicCodeNumber=0

profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
icon = os.path.join(home, 'icon.png')
FANART = os.path.join(home, 'fanart.jpg')

resolve_url = _core.get_resolve_url()
g_ignoreSetResolved = _core.get_resolve_url()
#BASE_URL = _core.get_base_url()
SOURCES = _core.get_sources()
FAV = _core.get_fav()
REMOTE_DBG = _core.get_remote_debug()

#########################################################
#                  INTERNAL FUNCTIONS                   #
#########################################################
# - All Params needed in root plugin dir                #
# - get_params, etc are here                            #
# - bye                                                 #
#########################################################

class InputWindow(xbmcgui.WindowDialog):
    def __init__(self, *args, **kwargs):
        self.cptloc = kwargs.get('captcha')
        self.img = xbmcgui.ControlImage(335,30,624,60,self.cptloc)
        self.addControl(self.img)
        self.kbd = xbmc.Keyboard()

    def get(self):
        self.show()
        time.sleep(2)
        self.kbd.doModal()
        if (self.kbd.isConfirmed()):
            text = self.kbd.getText()
            self.close()
            return text
        self.close()
        return False

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def getFavorites():
        items = json.loads(open(favorites).read())
        total = len(items)
        for i in items:
            name = i[0]
            url = i[1]
            iconimage = i[2]
            try:
                fanArt = i[3]
                if fanArt == None:
                    raise
            except:
                if addon.getSetting('use_thumb') == "true":
                    fanArt = iconimage
                else:
                    fanArt = fanart
            try: playlist = i[5]
            except: playlist = None
            try: regexs = i[6]
            except: regexs = None

            if i[4] == 0:
                addLink(url,name,iconimage,fanArt,'','','','fav',playlist,regexs,total)
            else:
                addDir(name,url,i[4],iconimage,fanart,'','','','','fav')

def addFavorite(name,url,iconimage,fanart,mode,playlist=None,regexs=None):
        favList = []
        try:
            # seems that after
            name = name.encode('utf-8', 'ignore')
        except:
            pass
        if os.path.exists(favorites)==False:
            _core.addon_log('Making Favorites File')
            favList.append((name,url,iconimage,fanart,mode,playlist,regexs))
            a = open(favorites, "w")
            a.write(json.dumps(favList))
            a.close()
        else:
            _core.addon_log('Appending Favorites')
            a = open(favorites).read()
            data = json.loads(a)
            data.append((name,url,iconimage,fanart,mode))
            b = open(favorites, "w")
            b.write(json.dumps(data))
            b.close()

def rmFavorite(name):
        data = json.loads(open(favorites).read())
        for index in range(len(data)):
            if data[index][0]==name:
                del data[index]
                b = open(favorites, "w")
                b.write(json.dumps(data))
                b.close()
                break
        xbmc.executebuiltin("XBMC.Container.Refresh")

def urlsolver(url):
    import resolveurl
    host = resolveurl.HostedMediaFile(url)
    if host:
        resolver = resolveurl.resolve(url)
        resolved = resolver
        if isinstance(resolved,list):
            for k in resolved:
                quality = addon.getSetting('quality')
                if k['quality'] == 'HD'  :
                    resolver = k['url']
                    break
                elif k['quality'] == 'SD' :
                    resolver = k['url']
                elif k['quality'] == '1080p' and addon.getSetting('1080pquality') == 'true' :
                    resolver = k['url']
                    break
        else:
            resolver = resolved
    else:
        xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,resolveurl donot support this domain. - ,5000)")
        resolver=url
    return resolver

def download_file(name, url):    
        if addon.getSetting('save_location') == "":
            xbmc.executebuiltin("XBMC.Notification('LiveStreamsPro','Choose a location to save files.',15000,"+icon+")")
            addon.openSettings()
        params = {'url': url, 'download_path': addon.getSetting('save_location')}
        downloader.download(name, params)
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('LiveStreamsPro', 'Do you want to add this file as a source?')
        if ret:
            _core.addSource(os.path.join(addon.getSetting('save_location'), name), media_type=="download")

def _source_search(search_object=None, search_content="all"):
    names = ['Tutto', 'Live TV', 'Video on Demand', 'Sport', 'Download File', 'Other']
    types = ['all', 'ltv', 'vod', 'sport', 'download', 'other']
    dialog = xbmcgui.Dialog()
    index = dialog.select('Select what your content is', names)
    if index >= 0:
        search_content = types[index]

    import search as s
    if search_object is None:
        search_object = keyboard_user()
    if s.search(name=search_object, content=search_content):
        url = os.path.join(profile, "search_result.xml")
        _core.getData(url, FANART)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def _search(url,name):
   # print url,name
    pluginsearchurls = ['plugin://plugin.video.live.streamspro/?mode=400',\
             'VideoLibrary.Search',\
             'plugin://plugin.video.youtube/kodion/search/list/',\
             'plugin://plugin.video.dailymotion_com/?mode=search&amp;url',\
             'plugin://plugin.video.vimeo/kodion/search/list/',\
             'plugin://plugin.video.raitv/?mode=ondemand_search_by_name',\
             'plugin://plugin.video.cartoonhdtwo/?description&amp;fanart&amp;iconimage&amp;mode=3&amp;name=Search&amp;url=url'\
             ]
    names = ['Live Streams Pro', 'Kodi' ,'Youtube','DailyMotion','Vimeo', 'Rai on Demand','Cartoon Network']
    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose a video source', names)

    if index == 0:
        _source_search()
    if index == 1:
        xbmc.executebuiltin('VideoLibrary.Search')
    if index >= 2:
        url = pluginsearchurls[index]
        _core.pluginquerybyJSON(url)

def addDir(name,url,mode,iconimage,fanart,description,genre,date,credits,showcontext=False,regexs=None,reg_url=None,allinfo={}):

        #print 'addDir'

        if regexs and len(regexs)>0:
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)+"&regexs="+regexs
        else:
            u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)
        
        ok=True
        if date == '':
            date = None
        else:
            description += '\n\nDate: %s' %date
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if len(allinfo) <1 :
            liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "dateadded": date, "credits": credits })
        else:
            liz.setInfo(type="Video", infoLabels= allinfo)
        liz.setProperty("Fanart_Image", fanart)
        if showcontext:
            contextMenu = []
            parentalblock =addon.getSetting('parentalblocked')
            parentalblock= parentalblock=="true"
            parentalblockedpin =addon.getSetting('parentalblockedpin')
            if len(parentalblockedpin)>0:
                if parentalblock:
                    contextMenu.append(('Disable Parental Block','XBMC.RunPlugin(%s?mode=55&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))
                else:
                    contextMenu.append(('Enable Parental Block','XBMC.RunPlugin(%s?mode=56&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))
                    
            if showcontext == 'source':
            
                if name in str(SOURCES):
                    contextMenu.append(('Remove from Sources','XBMC.RunPlugin(%s?mode=8&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))
                    
                    
            elif showcontext == 'download':
                contextMenu.append(('Download','XBMC.RunPlugin(%s?url=%s&mode=9&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
            elif showcontext == 'fav':
                contextMenu.append(('Remove from LiveStreamsPro Favorites','XBMC.RunPlugin(%s?mode=6&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(name))))
            if showcontext == '!!update':
                fav_params2 = (
                    '%s?url=%s&mode=17&regexs=%s'
                    %(sys.argv[0], urllib.quote_plus(reg_url), regexs)
                    )
                contextMenu.append(('[COLOR yellow]!!update[/COLOR]','XBMC.RunPlugin(%s)' %fav_params2))
            if not name in FAV:
                contextMenu.append(('Add to LiveStreamsPro Favorites','XBMC.RunPlugin(%s?mode=5&name=%s&url=%s&iconimage=%s&fanart=%s&fav_mode=%s)'
                         %(sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(fanart), mode)))
            liz.addContextMenuItems(contextMenu)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def ytdl_download(url,title,media_type='video'):
    # play in xbmc while playing go back to contextMenu(c) to "!!Download!!"
    # Trial yasceen: seperate |User-Agent=
    import youtubedl
    
    if not url == '':
        if media_type== 'audio':
            youtubedl.single_YD(url,download=True,audio=True)
        else:
            youtubedl.single_YD(url,download=True)
    elif xbmc.Player().isPlaying() == True :
        import YDStreamExtractor
        if YDStreamExtractor.isDownloading() == True:

            YDStreamExtractor.manageDownloads()
        else:
            xbmc_url = xbmc.Player().getPlayingFile()

            xbmc_url = xbmc_url.split('|User-Agent=')[0]
            info = {'url':xbmc_url,'title':title,'media_type':media_type}
            youtubedl.single_YD('',download=True,dl_info=info)
    else:
        xbmc.executebuiltin("XBMC.Notification(DOWNLOAD,First Play [COLOR yellow]WHILE playing download[/COLOR] ,10000)")

## Lunatixz PseudoTV feature
def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string

def uni(string, encoding = 'utf-8'):
    if isinstance(string, basestring):
        if not isinstance(string, unicode):
            string = unicode(string, encoding, 'ignore')
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def sendJSON( command):
    data = ''
    try:
        data = xbmc.executeJSONRPC(uni(command))
    except UnicodeEncodeError:
        data = xbmc.executeJSONRPC(ascii(command))

    return uni(data)

def pluginquerybyJSON(url,give_me_result=None,playlist=False):
    if 'audio' in url:
        json_query = uni('{"jsonrpc":"2.0","method":"Files.GetDirectory","params": {"directory":"%s","media":"video", "properties": ["title", "album", "artist", "duration","thumbnail", "year"]}, "id": 1}') %url
    else:
        json_query = uni('{"jsonrpc":"2.0","method":"Files.GetDirectory","params":{"directory":"%s","media":"video","properties":[ "plot","playcount","director", "genre","votes","duration","trailer","premiered","thumbnail","title","year","dateadded","fanart","rating","season","episode","studio","mpaa"]},"id":1}') %url
    json_folder_detail = json.loads(sendJSON(json_query))
    #print json_folder_detail
    if give_me_result:
        return json_folder_detail
    if json_folder_detail.has_key('error'):
        return
    else:

        for i in json_folder_detail['result']['files'] :
            meta ={}
            url = i['file']
            name = removeNonAscii(i['label'])
            thumbnail = removeNonAscii(i['thumbnail'])
            fanart = removeNonAscii(i['fanart'])
            meta = dict((k,v) for k, v in i.iteritems() if not v == '0' or not v == -1 or v == '')
            meta.pop("file", None)
            if i['filetype'] == 'file':
                if playlist:
                    _core.play_playlist(name,url,queueVideo='1')
                    continue
                else:
                    addLink(url,name,thumbnail,fanart,'','','','',None,'',total=len(json_folder_detail['result']['files']),allinfo=meta)
                    #xbmc.executebuiltin("Container.SetViewMode(500)")
                    if i['type'] and i['type'] == 'tvshow' :
                        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
                    elif i['episode'] > 0 :
                        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

            else:
                addDir(name,url,53,thumbnail,fanart,'','','','',allinfo=meta)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addLink(url,name,iconimage,fanart,description,genre,date,showcontext,playlist,regexs,total,setCookie="",allinfo={}):
        #print 'url,name,regex',url,name,iconimage,regexs
        contextMenu =[]
        parentalblock =addon.getSetting('parentalblocked')
        parentalblock= parentalblock=="true"
        parentalblockedpin =addon.getSetting('parentalblockedpin')
        if len(parentalblockedpin)>0:
            if parentalblock:
                contextMenu.append(('Disable Parental Block','XBMC.RunPlugin(%s?mode=55&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))
            else:
                contextMenu.append(('Enable Parental Block','XBMC.RunPlugin(%s?mode=56&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))
                    
        try:
            name = name.encode('utf-8')
        except: pass
        ok = True
        isFolder=False
        if regexs:
            mode = '17'
            if 'listrepeat' in regexs:
                isFolder=True
            contextMenu.append(('[COLOR white]!!Download Currently Playing!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=21&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
        elif  (any(x in url for x in resolve_url) and  url.startswith('http')) or url.endswith('&mode=19'):
            url=url.replace('&mode=19','')
            mode = '19'
            contextMenu.append(('[COLOR white]!!Download Currently Playing!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=21&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
        elif url.endswith('&mode=18'):
            url=url.replace('&mode=18','')
            mode = '18'
            contextMenu.append(('[COLOR white]!!Download!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=23&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
            if addon.getSetting('dlaudioonly') == 'true':
                contextMenu.append(('!!Download [COLOR seablue]Audio!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=24&name=%s)'
                                        %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
        elif url.endswith('&mode=20'):
            url=url.replace('&mode=20','')
            mode = '20'
        elif url.endswith('&mode=22'):
            url=url.replace('&mode=22','')
            mode = '22'      
        elif url.startswith('magnet:?xt='):
            if '&' in url and not '&amp;' in url :
                url = url.replace('&','&amp;')
            url = 'plugin://plugin.video.pulsar/play?uri=' + url
            mode = '12'
        else:
            mode = '12'
            contextMenu.append(('[COLOR white]!!Download Currently Playing!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=21&name=%s)'
                                    %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
        if 'plugin://plugin.video.youtube/play/?video_id=' in url:
              yt_audio_url = url.replace('plugin://plugin.video.youtube/play/?video_id=','https://www.youtube.com/watch?v=')
              contextMenu.append(('!!Download [COLOR blue]Audio!![/COLOR]','XBMC.RunPlugin(%s?url=%s&mode=24&name=%s)'
                                      %(sys.argv[0], urllib.quote_plus(yt_audio_url), urllib.quote_plus(name))))
        u=sys.argv[0]+"?"
        play_list = False
        
        if playlist:
            if addon.getSetting('add_playlist') == "false" and '$$LSPlayOnlyOne$$' not in playlist[0] :
                u += "url="+urllib.quote_plus(url)+"&mode="+mode
            else:
                u += "mode=13&name=%s&playlist=%s" %(urllib.quote_plus(name), urllib.quote_plus(str(playlist).replace(',','||')))
                name = name + '[COLOR magenta] (' + str(len(playlist)) + ' items )[/COLOR]'
                play_list = True
        elif mode=='22' or (mode=='17' and url.endswith('&mode=22')):             
            u += "url="+urllib.quote_plus(url)+"&name="+urllib.quote(name)+"&mode="+mode
        else:
            u += "url="+urllib.quote_plus(url)+"&mode="+mode
        if regexs:
            u += "&regexs="+regexs
        if not setCookie == '':
            u += "&setCookie="+urllib.quote_plus(setCookie)
        if iconimage and  not iconimage == '':
            u += "&iconimage="+urllib.quote_plus(iconimage)
            
        if date == '':
            date = None
        else:
            description += '\n\nDate: %s' %date
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)

        #if isFolder:
        if allinfo==None or len(allinfo) <1:
            liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "dateadded": date })
        else:
            liz.setInfo(type="Video", infoLabels=allinfo)
        liz.setProperty("Fanart_Image", fanart)
 
        if (not play_list) and not any(x in url for x in g_ignoreSetResolved) and not '$PLAYERPROXY$=' in url and not (mode=='22' or (mode=='17' and url.endswith('&mode=22'))):#  (not url.startswith('plugin://plugin.video.f4mTester')):
            if regexs:
                #print urllib.unquote_plus(regexs)
                if '$pyFunction:playmedia(' not in urllib.unquote_plus(regexs) and 'notplayable' not in urllib.unquote_plus(regexs) and 'listrepeat' not in  urllib.unquote_plus(regexs) :
                    #print 'setting isplayable',url, urllib.unquote_plus(regexs),url
                    liz.setProperty('IsPlayable', 'true')
            else:
                liz.setProperty('IsPlayable', 'true')
                
        else:
            _core.addon_log('NOT setting isplayable'+url)
        
        if showcontext:
            #contextMenu = []
            if showcontext == 'fav':
                contextMenu.append(
                    ('Remove from LiveStreamsPro Favorites','XBMC.RunPlugin(%s?mode=6&name=%s)'
                     %(sys.argv[0], urllib.quote_plus(name)))
                     )
            elif not name in FAV:
                try:
                    fav_params = (
                        '%s?mode=5&name=%s&url=%s&iconimage=%s&fanart=%s&fav_mode=0'
                        %(sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(fanart))
                        )
                except:
                    fav_params = (
                        '%s?mode=5&name=%s&url=%s&iconimage=%s&fanart=%s&fav_mode=0'
                        %(sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage.encode("utf-8")), urllib.quote_plus(fanart.encode("utf-8")))
                        )
                if playlist:
                    fav_params += 'playlist='+urllib.quote_plus(str(playlist).replace(',','||'))
                if regexs:
                    fav_params += "&regexs="+regexs
                contextMenu.append(('Add to LiveStreamsPro Favorites','XBMC.RunPlugin(%s)' %fav_params))
            liz.addContextMenuItems(contextMenu)
        try:
            if not playlist is None:
                if addon.getSetting('add_playlist') == "false":
                    playlist_name = name.split(') ')[1]
                    contextMenu_ = [
                        ('Play '+playlist_name+' PlayList','XBMC.RunPlugin(%s?mode=13&name=%s&playlist=%s)'
                         %(sys.argv[0], urllib.quote_plus(playlist_name), urllib.quote_plus(str(playlist).replace(',','||'))))
                         ]
                    liz.addContextMenuItems(contextMenu_)
        except: pass
        #print 'adding',name
    
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,totalItems=total,isFolder=isFolder)

        #print 'added',name
        return ok

def d2x(d, root="root",nested=0):

    op = lambda tag: '<' + tag + '>'
    cl = lambda tag: '</' + tag + '>\n'

    ml = lambda v,xml: xml + op(key) + str(v) + cl(key)
    xml = op(root) + '\n' if root else ""

    for key,vl in d.iteritems():
        vtype = type(vl)
        if nested==0: key='regex' #enforcing all top level tags to be named as regex
        if vtype is list: 
            for v in vl:
                v=escape(v)
                xml = ml(v,xml)         
        
        if vtype is dict: 
            xml = ml('\n' + d2x(vl,None,nested+1),xml)         
        if vtype is not list and vtype is not dict: 
            if not vl is None: vl=escape(vl)
            #print repr(vl)
            if vl is None:
                xml = ml(vl,xml)
            else:
                #xml = ml(escape(vl.encode("utf-8")),xml)
                xml = ml(vl.encode("utf-8"),xml)

    xml += cl(root) if root else ""

    return xml

def keyboard_user(msg=""):
    text_input = None
    if not text_input:
        keyboard = xbmc.Keyboard('', msg)
        keyboard.doModal()
        if keyboard.isConfirmed():
            text_input = keyboard.getText()
    return text_input

#########################################################
#              INTERNAL FUNCTIONS END                   #
#########################################################
# - All Params needed in root plugin dir                #
# - get_params, etc are here                            #
# - bye                                                 #
#########################################################

if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

try: xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
except: pass

try: xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
except:pass

try: xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
except: pass

try: xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
except: pass

params=get_params()

try: url=urllib.unquote_plus(params["url"]).decode('utf-8')
except: url=None

try: name=urllib.unquote_plus(params["name"])
except: name=None

try: iconimage=urllib.unquote_plus(params["iconimage"])
except: iconimage=None

try: fanart=urllib.unquote_plus(params["fanart"])
except: fanart=FANART

try: mode=int(params["mode"])
except: mode=None

try: playlist=eval(urllib.unquote_plus(params["playlist"]).replace('||',','))
except: playlist=None

try: fav_mode=int(params["fav_mode"])
except: fav_mode=None

try: regexs=params["regexs"]
except: regexs=None

try: playitem=urllib.unquote_plus(params["playitem"])
except: playitem=''
   
_core.addon_log("Mode: "+str(mode))

if not url is None:
    _core.addon_log("URL: "+str(url.encode('utf-8')))
_core.addon_log("Name: "+str(name))

if not playitem =='':
    s=_core.getSoup('',data=playitem)
    name,url,regexs=_core.getItems(s,None,dontLink=True)
    mode=117

elif mode==99:
    #xbmcaddon.Addon("plugin.video.live.streamspro").openSettings()
    _core.addDir('Add Source Url', 'url', 87, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/impostazioni.png", FANART,'Configura Trakt.tv o TV Time per sincronizzare i contenuti che hai visto con il tuo provider remoto preferito!','','','', True)
    _core.addDir('Add Community Source', 'url', 10, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/impostazioni.png", FANART,'Configura Trakt.tv o TV Time per sincronizzare i contenuti che hai visto con il tuo provider remoto preferito!','','','', True)
    _core.addDir('Remove Source(s)', 'url', 88, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/impostazioni.png", FANART,'Configura Trakt.tv o TV Time per sincronizzare i contenuti che hai visto con il tuo provider remoto preferito!','','','', True)
    _core.addDir('Addon Setting', 'url', 96, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/impostazioni.png", FANART,'Configura Trakt.tv o TV Time per sincronizzare i contenuti che hai visto con il tuo provider remoto preferito!','','','', True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==98:
    line1 = "Live Streams Pro doesn't contain anthing, everything you can see here has been added by you."
    line2 = "So any copyright infringement is not cause of developers."
    xbmcgui.Dialog().ok("Live Streams Pro", line1, line2)

elif mode==97:
    autostart = addon.getSetting('autostart')
    if autostart == "true":
        path = os.path.join(xbmc.translatePath('special://userdata'),'autoexec.py')
        file = open(path, "w+") 
        file.write("import xbmc\n")
        file.write("xbmc.executebuiltin('XBMC.RunAddon(plugin.video.live.streamspro)')") 
        file.close() 
    if autostart == "false":
        path = os.path.join(xbmc.translatePath('special://userdata'),'autoexec.py')
        file = open(path, "w")
        file.close() 
    xbmcgui.Dialog().ok("Live Streams Pro", "Le impostazioni di avvio automatico sono state salvate!")

elif mode==96:
     xbmcaddon.Addon("plugin.video.live.streamspro").openSettings()

if mode==None:
    _core.addon_log("_core.homepage")
    #updater.check_for_updates()
    _core.homepage()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==400:
    _source_search()

if mode==100:
    _core.addon_log("_core.getSources")
    _core.getSources("all")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if mode==101:
    _core.addon_log("_core.getSources")
    _core.getSources("ltv")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if mode==102:
    _core.addon_log("_core.getSources")
    _core.getSources("vod")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if mode==103:
    _core.addon_log("_core.getSources")
    _core.getSources("sport")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if mode==104:
    _core.addon_log("_core.getSources")
    _core.getSources("other")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if mode==105:
    _core.addon_log("_core.getSources")
    _core.getSources("download")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==60:
    _core.addDir('Search in library', 'url', 61, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/cerca.png", FANART,'Cerca tra tutti i contenuti presenti nella tua libreria di Kodi, film e serie tv.','','','', True)
    _core.addDir('Movies', 'url', 62, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/film.png", FANART,'Sfoglia la tua libreria di film, scegli se cercare un titolo per nome, attore, genere e goditi lo spettacolo.','','','', True)
    _core.addDir('TV Shows', 'url', 63, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/tv.png", FANART,'Sfoglia la tua libreria di serie TV, scegli se cercare un titolo per nome, attore, genere e goditi lo spettacolo.','','','', True)
    _core.addDir('Favourites', 'url', 65, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/stella.png", FANART,'Sfoglia la lista dei tuoi preferiti interna di Kodi e gestisci i tuoi contenuti preferiti','','','', True)
    _core.addDir('Video Sources', 'url', 64, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/cartella.png", FANART,'Sfoglia, aggiungi e gestisci le directory sorgenti della tua libreria interna di Kodi.','','','', True)
    _core.addDir('Sync Content', 'url', 66, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/trakt.png", FANART,'Configura Trakt.tv o TV Time per sincronizzare i contenuti che hai visto con il tuo provider remoto preferito!','','','', True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==61:
    xbmc.executebuiltin('VideoLibrary.Search')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==62:
    xbmc.executebuiltin('ActivateWindow(Videos, videodb://movies/)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==63:
    xbmc.executebuiltin('ActivateWindow(Videos, videodb://tvshows/)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==64:
    xbmc.executebuiltin('ActivateWindow(Videos, sources://video/)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==65:
    xbmc.executebuiltin('ActivateWindow(Favourites)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==1:
    _core.addon_log("_core.getData")
    data=None
    
    if regexs and len(regexs)>0:
        data,setresolved=_core.getRegexParsed(regexs, url)
        if data.startswith('http') or data.startswith('smb') or data.startswith('nfs') or data.startswith('/'):
            url=data
            data=None
    _core.getData(url,fanart,data)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==2:
    _core.addon_log("_core.getChannelItems")
    _core.getChannelItems(name,url,fanart)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==3:
    _core.addon_log("_core.getSubChannelItems")
    _core.getSubChannelItems(name,url,fanart)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==4:
    try:
        _core.addon_log("getFavorites")
        getFavorites()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except:
        xbmcgui.Dialog().ok("Live Streams Pro", "No favs to show here dude") 

elif mode==5:
    _core.addon_log("addFavorite")
    
    try: name = name.split('\\ ')[1]
    except: pass
    
    try: name = name.split('  - ')[0]
    except: pass
    
    addFavorite(name,url,iconimage,fanart,fav_mode)

elif mode==6:
    _core.addon_log("rmFavorite")
    try:
        name = name.split('\\ ')[1]
    except:
        pass
    try:
        name = name.split('  - ')[0]
    except:
        pass
    rmFavorite(name)

elif mode==7:
    _core.addon_log("_core.addSource")
    if int(addon.getSetting("choose_source")) == 0:
        url = addon.getSetting("new_file_source")
    elif int(addon.getSetting("choose_source")) == 1:
        url = addon.getSetting("new_url_source")
    _core.addSource(url)

elif mode==77:
    _core.addon_log("_core.addSourceFromAList")
    if int(addon.getSetting("choose_folder_source")) == 0:
        url = addon.getSetting("new_folder_file_source")
    elif int(addon.getSetting("choose_folder_source")) == 1:
        url = addon.getSetting("new_folder_url_source")
    _core.addSourceFromAList(url)

elif mode==777:
    _core.addon_log("Purge Lists")
    _core.purgeLists()

elif mode==87:
    _core.addon_log("_core.addSourceWizard")
    _core.addSourceWizard()

elif mode==88:
    _core.addon_log("_core.rmSource")
    _core.rmSourceWithWizard()

elif mode==8:
    _core.addon_log("_core.rmSource")
    _core.rmSource(name)

elif mode==9:
    _core.addon_log("download_file")
    download_file(name, url)

elif mode==10:
    _core.addon_log("_core.getCommunitySources")
    _core.getCommunitySources()

elif mode==11:
    _core.addon_log("_core.addSource")
    url = addon.getSetting("new_url_source")
    _core.addSource(url)

elif mode==12:
    _core.addon_log("_core.setResolvedUrl")
    if not url.startswith("plugin://plugin") or not any(x in url for x in g_ignoreSetResolved):#not url.startswith("plugin://plugin.video.f4mTester") :
        setres=True
        if '$$LSDirect$$' in url:
            url=url.replace('$$LSDirect$$','')
            setres=False
        item = xbmcgui.ListItem(path=url)
        if setres:
            if addon.getSetting("use_internal_player") == "true":
                import  CustomPlayer
                player = CustomPlayer.MyXBMCPlayer()
                player.url=url
                #xbmc.Player().play(url)
                player.play(url)
                
            else:
                xbmc.Player().play(url)
        else: 
            if addon.getSetting("use_internal_player") == "true":
                import  CustomPlayer
                player = CustomPlayer.MyXBMCPlayer()
                player.url=url
                #xbmc.Player().play(url)
                player.play(url)
                
            else:
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    else:
#        print 'Not setting setResolvedUrl'
        xbmc.executebuiltin('XBMC.RunPlugin('+url+')')

elif mode==13:
    _core.addon_log("play_playlist")
    _core.play_playlist(name, playlist)

elif mode==14:
    _core.addon_log("_core.get_xml_database")
    _core.get_xml_database(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==15:
    _core.addon_log("browse_xml_database")
    _core.get_xml_database(url, True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==16:
    _core.addon_log("browse_community")
    _core.getCommunitySources(url,browse=True)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==17 or mode==117:
    _core.addon_log("_core.getRegexParsed")
    #print '_core.getRegexParsed'
    data=None
    if regexs and 'listrepeat' in urllib.unquote_plus(regexs):
        listrepeat,ret,m,regexs, cookieJar =_core.getRegexParsed(regexs, url)
        #print listrepeat,ret,m,regexs
        d=''
        regexname=m['name']
        existing_list=regexs.pop(regexname)
        url=''
        import copy
        ln=''
        rnumber=0
        for obj in ret:
            #print 'obj',obj
            try:
                rnumber+=1
                newcopy=copy.deepcopy(regexs)
                listrepeatT=listrepeat
                i=0
                for i in range(len(obj)):
                    if len(newcopy)>0:
                        for the_keyO, the_valueO in newcopy.iteritems():
                            if the_valueO is not None:
                                for the_key, the_value in the_valueO.iteritems():
                                    if the_value is not None:                                
                                        if type(the_value) is dict:
                                            for the_keyl, the_valuel in the_value.iteritems():
                                                if the_valuel is not None:
                                                    val=None
                                                    if isinstance(obj,tuple):                                                    
                                                        try:
                                                           val= obj[i].decode('utf-8') 
                                                        except: 
                                                            val= obj[i] 
                                                    else:
                                                        try:
                                                            val= obj.decode('utf-8') 
                                                        except:
                                                            val= obj
                                                    
                                                    if '[' + regexname+'.param'+str(i+1) + '][DE]' in the_valuel:
                                                        the_valuel=the_valuel.replace('[' + regexname+'.param'+str(i+1) + '][DE]', unescape(val))
                                                    the_value[the_keyl]=the_valuel.replace('[' + regexname+'.param'+str(i+1) + ']', val)
                                                    #print 'first sec',the_value[the_keyl]
                                                    
                                        else:
                                            val=None
                                            if isinstance(obj,tuple):
                                                try:
                                                     val=obj[i].decode('utf-8') 
                                                except:
                                                    val=obj[i] 
                                            else:
                                                try:
                                                    val= obj.decode('utf-8') 
                                                except:
                                                    val= obj
                                            if '[' + regexname+'.param'+str(i+1) + '][DE]' in the_value:
                                                #print 'found DE',the_value.replace('[' + regexname+'.param'+str(i+1) + '][DE]', unescape(val))
                                                the_value=the_value.replace('[' + regexname+'.param'+str(i+1) + '][DE]', unescape(val))

                                            the_valueO[the_key]=the_value.replace('[' + regexname+'.param'+str(i+1) + ']', val)
                                            #print 'second sec val',the_valueO[the_key]

                    val=None
                    if isinstance(obj,tuple):
                        try:
                            val=obj[i].decode('utf-8')
                        except:
                            val=obj[i]
                    else:
                        try:
                            val=obj.decode('utf-8')
                        except: 
                            val=obj
                    if '[' + regexname+'.param'+str(i+1) + '][DE]' in listrepeatT:
                        listrepeatT=listrepeatT.replace('[' + regexname+'.param'+str(i+1) + '][DE]',val)
                    listrepeatT=listrepeatT.replace('[' + regexname+'.param'+str(i+1) + ']',escape(val))
                listrepeatT=listrepeatT.replace('[' + regexname+'.param'+str(0) + ']',str(rnumber)) 
                
                try:
                    if cookieJar and '[' + regexname+'.cookies]' in listrepeatT:
                        listrepeatT=listrepeatT.replace('[' + regexname+'.cookies]',_core.getCookiesString(cookieJar)) 
                except: pass
                
                regex_xml=''
                if len(newcopy)>0:
                    regex_xml=d2x(newcopy,'lsproroot')
                    regex_xml=regex_xml.split('<lsproroot>')[1].split('</lsproroot')[0]
              
                #ln+='\n<item>%s\n%s</item>'%(listrepeatT.encode("utf-8"),regex_xml)   
                try:
                    ln+='\n<item>%s\n%s</item>'%(listrepeatT,regex_xml)
                except: ln+='\n<item>%s\n%s</item>'%(listrepeatT.encode("utf-8"),regex_xml)
            except: traceback.print_exc(file=sys.stdout)
        _core.addon_log(repr(ln))
        _core.getData('','',ln)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    else:
        url,setresolved = _core.getRegexParsed(regexs, url)
        #print 'imhere', repr(url),setresolved,name
        #print 'imhere'
        if not (regexs and 'notplayable' in regexs and not url):        
            if url:
                if '$PLAYERPROXY$=' in url:
                    url,proxy=url.split('$PLAYERPROXY$=')
                    print 'proxy',proxy
                    #Jairox mod for proxy auth
                    proxyuser = None
                    proxypass = None
                    if len(proxy) > 0 and '@' in proxy:
                        proxy = proxy.split(':')
                        proxyuser = proxy[0]
                        proxypass = proxy[1].split('@')[0]
                        proxyip = proxy[1].split('@')[1]
                        port = proxy[2]
                    else:
                        proxyip,port=proxy.split(':')

                    _core.playmediawithproxy(url,name,iconimage,proxyip,port, proxyuser,proxypass) #jairox
                else:
                    _core.playsetresolved(url,name,iconimage,setresolved,regexs)
            else:
                xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Failed to extract regex. - "+"this"+",4000,"+icon+")")

elif mode==18:
    _core.addon_log("youtubedl")
    try:
        import youtubedl
    except Exception:
        xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Please [COLOR yellow]install Youtube-dl[/COLOR] module ,10000,"")")
    stream_url=youtubedl.single_YD(url)
    _core.playsetresolved(stream_url,name,iconimage)

elif mode==19:
    _core.addon_log("Genesiscommonresolvers")
    _core.playsetresolved (urlsolver(url),name,iconimage,True)

elif mode==20:
    _core.addon_log("setResolvedUrl")
    item = xbmcgui.ListItem(path=url)
    if '|' in url:
        url,strhdr = url.split('|')
        item.setProperty('inputstream.adaptive.stream_headers', strhdr)
        item.setPath(url)
    if '.m3u8' in url:
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        item.setMimeType('application/vnd.apple.mpegstream_url')
        item.setContentLookup(False)
   
    elif '.mpd' in url:
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        item.setMimeType('application/dash+xml')
        item.setContentLookup(False)
    
    elif '.ism' in url:
        item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        item.setProperty('inputstream.adaptive.manifest_type', 'ism')
        item.setMimeType('application/vnd.ms-sstr+xml')
        item.setContentLookup(False)

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

elif mode==21:
    _core.addon_log("download current file using youtube-dl service")
    mtype='video'
    if '[mp3]' in name:
        mtype='audio'
        name=name.replace('[mp3]','')
    ytdl_download('',name, mtype)

elif mode==22:
    print "slproxy"
    try:
        from dsp import streamlink_proxy
        slProxy = streamlink_proxy.SLProxy_Helper()
        try:
            q =  re.findall(r'\$\$QUALITY=([^\$\$]+)\$\$', url)[0]
        except:
            q = 'best'
        url = re.sub(r'\$\$QUALITY=.*?\$\$', '', url)
        url = urllib.quote(url)+'&amp;q=%s'%q
        listitem = xbmcgui.ListItem(str(name))
        listitem.setInfo('video', {'Title': str(name)})
        listitem.setPath(url)                          
        slProxy.playSLink(url, listitem)
    except:
        pass

elif mode==23:
    _core.addon_log("get info then download")
    mtype='video'
    if '[mp3]' in name:
        mtype='audio'
        name=name.replace('[mp3]','')
    ytdl_download(url,name,mtype)

elif mode==24:
    _core.addon_log("Audio only youtube download")
    ytdl_download(url,name,'audio')

elif mode==25:
    _core.addon_log("Searchin Other plugins")
    _search(url,name)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==55:
    _core.addon_log("enabled lock")
    parentalblockedpin =addon.getSetting('parentalblockedpin')
    keyboard = xbmc.Keyboard('','Enter Pin')
    keyboard.doModal()
    if not (keyboard.isConfirmed() == False):
        newStr = keyboard.getText()
        if newStr==parentalblockedpin:
            addon.setSetting('parentalblocked', "false")
            xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Parental Block Disabled,5000,"+icon+")")
        else:
            xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Wrong Pin??,5000,"+icon+")")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
elif mode==56:
    _core.addon_log("disable lock")
    addon.setSetting('parentalblocked', "true")
    xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Parental block enabled,5000,"+icon+")")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode==53:
    _core.addon_log("Requesting JSON-RPC Items")
    pluginquerybyJSON(url)
    #xbmcplugin.endOfDirectory(int(sys.argv[1]))

if not viewmode==None:
   print 'setting view mode'
   xbmc.executebuiltin("Container.SetViewMode(%s)"%viewmode)
    