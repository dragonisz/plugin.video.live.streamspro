# -*- coding: utf-8 -*-
import urllib, urllib2
import re, os, sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
import traceback
import cookielib, traceback, base64

addon = xbmcaddon.Addon('plugin.video.live.streamspro')
sys.path.append(xbmc.translatePath(os.path.join(xbmc.translatePath(addon.getAddonInfo('Path')), 'lib')))

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
try:
    from xml.sax.saxutils import escape
except: traceback.print_exc()
try:
    import json
except:
    import simplejson as json
import SimpleDownloader as downloader
import time

addon_version = addon.getAddonInfo('version')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
REV = os.path.join(profile, 'list_revision')
icon = os.path.join(home, 'icon.png')
FANART = os.path.join(home, 'fanart.jpg')
source_file = os.path.join(profile, 'source_file')
functions_dir = profile

communityfiles = os.path.join(profile, 'LivewebTV')
downloader = downloader.SimpleDownloader()
debug = addon.getSetting('debug')

if os.path.exists(favorites)==True:
    FAV = open(favorites).read()
else: FAV = []
    
if os.path.exists(source_file)==True:
    SOURCES = open(source_file).read()
else: SOURCES = []

iid = 0
resolve_url = ['180upload.com', 'allmyvideos.net', 'bestreams.net', 'clicknupload.com', 'cloudzilla.to', 'movshare.net', 'novamov.com', 'nowvideo.sx', 'videoweed.es', 'daclips.in', 'datemule.com', 'fastvideo.in', 'faststream.in', 'filehoot.com', 'filenuke.com', 'sharesix.com',  'plus.google.com', 'picasaweb.google.com', 'gorillavid.com', 'gorillavid.in', 'grifthost.com', 'hugefiles.net', 'ipithos.to', 'ishared.eu', 'kingfiles.net', 'mail.ru', 'my.mail.ru', 'videoapi.my.mail.ru', 'mightyupload.com', 'mooshare.biz', 'movdivx.com', 'movpod.net', 'movpod.in', 'movreel.com', 'mrfile.me', 'nosvideo.com', 'openload.io', 'played.to', 'bitshare.com', 'filefactory.com', 'k2s.cc', 'oboom.com', 'rapidgator.net', 'primeshare.tv', 'bitshare.com', 'filefactory.com', 'k2s.cc', 'oboom.com', 'rapidgator.net', 'sharerepo.com', 'stagevu.com', 'streamcloud.eu', 'streamin.to', 'thefile.me', 'thevideo.me', 'tusfiles.net', 'uploadc.com', 'zalaa.com', 'uploadrocket.net', 'uptobox.com', 'v-vids.com', 'veehd.com', 'vidbull.com', 'videomega.tv', 'vidplay.net', 'vidspot.net', 'vidto.me', 'vidzi.tv', 'vimeo.com', 'vk.com', 'vodlocker.com', 'xfileload.com', 'xvidstage.com', 'zettahost.tv']
g_ignoreSetResolved = ['plugin.video.dramasonline','plugin.video.f4mTester','plugin.video.shahidmbcnet','plugin.video.SportsDevil','plugin.stream.vaughnlive.tv','plugin.video.ZemTV-shani']
REMOTE_DBG=False
fanart=FANART

def get_resolve_url():
    return resolve_url

def ignore_set_resolved():
    return g_ignoreSetResolved

def get_sources():
    return SOURCES

#def get_base_url():
#    return BASE_URL

def get_fav():
    return FAV

def get_remote_debug():
    return REMOTE_DBG

def get_localized_string(code):
    addon = xbmcaddon.Addon('plugin.video.live.streamspro')
    string_translated = addon.getLocalizedString(code)
    try: string_translated = dev.encode("utf-8")
    except: pass
    return string_translated

class NoRedirection(urllib2.HTTPErrorProcessor):
   def http_response(self, request, response):
       return response
   https_response = http_response

def addon_log(string):
    if debug == 'true':
        xbmc.log("[addon.live.streamspro-%s]: %s" %(addon_version, string))

def makeRequest(url, headers=None):
        try:
            if headers is None:
                headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}            
            if '|' in url:
                url,header_in_page=url.split('|')
                header_in_page=header_in_page.split('&')
                
                for h in header_in_page:
                    if len(h.split('='))==2:
                        n,v=h.split('=')
                    else:
                        vals=h.split('=')
                        n=vals[0]
                        v='='.join(vals[1:])
                        #n,v=h.split('=')
                    print n,v
                    headers[n]=v
            
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
            return data
        except urllib2.URLError, e:
            addon_log('URL: '+url)
            if hasattr(e, 'code'):
                addon_log('We failed with error code - %s.' % e.code)
                xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,We failed with error code - "+str(e.code)+",10000,"+icon+")")
            elif hasattr(e, 'reason'):
                addon_log('We failed to reach a server.')
                addon_log('Reason: %s' %e.reason)
                xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,We failed to reach a server. - "+str(e.reason)+",10000,"+icon+")")

def homepage():
    if addon.getSetting("searchotherplugins") == "true":
        addDir(get_localized_string(30000), 'url', 25, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/cerca.png", FANART,'Cerca tra tutti i contenuti disponibili e proposti su Live Streams Pro.','','','', True)
    if addon.getSetting("enable_ltv_menu") == "true":
        addDir(get_localized_string(30002), 'url', 101, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/tv.png", FANART,'Naviga tra le TV disponibili per canale o tramite un efficiente sistema di ricerca.','','','', True)
    if addon.getSetting("enable_vod_menu") == "true":
        addDir(get_localized_string(30004), 'url', 102, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/film.png", FANART,'Una vagonata di contenuti disponibili on Demand, utilizza il sistema di ricerca integrato in Kodi o sfoglia le liste!','','','', True)
    if addon.getSetting("enable_sport_menu") == "true":
        addDir(get_localized_string(30006), 'url', 103, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/notizie.png", FANART,'Tutti i canali dedicati agli eventi sportivi in diretta e non.','','','', True) 
    if addon.getSetting("enable_other_menu") == "true":
        addDir(get_localized_string(30008), 'url', 104, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/mondo.png", FANART,'Qui sono presenti tutti i contenuti non catalogati o non catalogabili nelle sezioni soprastanti.','','','', True)
    if addon.getSetting("enable_source_menu") == "true":
        addDir(get_localized_string(30010), 'url', 100, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/link.png", FANART,'Sfoglia la lista di tutti i tuoi contenuti personali e gestiscili da qui.','','','', True)
    if addon.getSetting("enable_download_menu") == "true" and addon.getSetting('save_location') != "":
        addDir(get_localized_string(30012), 'url', 105, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/download.png", FANART,'Qui sono presenti tutti i contenuti scaricati tramite Live Streams Pro','','','', True)
    if addon.getSetting("enable_favs_menu") == "true":
        addDir(get_localized_string(30014), 'url', 4, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/stella.png", FANART,'Goditi tutti i tuoi contenuti aggiunti ai preferiti di Live Streams Pro','','','', "fav")
    if addon.getSetting("enable_kodi_library") == "true":
        addDir(get_localized_string(30016), 'url', 60, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/cinema.png", FANART,'Sfoglia la libreria interna di Kodi, goditi tutti i tuoi contenuti, locali e non.','','','', True)
    if addon.getSetting("enable_settings_menu") == "true":
        addDir(get_localized_string(30018), 'url', 99, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/impostazioni.png", FANART,'Configura e aggiorna tutte le impostazioni di Live Streams Pro secondo le tue preferenze.','','','',True)
    addDir(get_localized_string(30020),'url', 98, "https://raw.githubusercontent.com/cttynul/xbmcttynul/master/media/menu/aiuto.png", FANART,'Live Streams Pro non contiene alcun contenuto, tutti i contenuti qui proposti sono facilmente reperibili sul web estratti e proposti in una forma piu user-friendly mediante sistema di web scraping.','','','',True)


def getSources(selection="other"):
        try:
            if addon.getSetting("browse_xml_database") == "true":
                addDir('XML Database','http://xbmcplus.xb.funpic.de/www-data/filesystem/',15,icon,FANART,'','','','')
            if addon.getSetting("browse_community") == "true":
                addDir('Community Files','community_files',16,icon,FANART,'','','','')
            if addon.getSetting("searchotherplugins") == "true":
                addDir('Global Search','Search Plugins',25,icon,FANART,'','','','')
            if os.path.exists(source_file)==True:
                sources = json.loads(open(source_file,"r").read())
                #print 'sources',sources
                if len(sources) > 1:
                    for i in sources:
                        try:
                            ## for pre 1.0.8 sources
                            if isinstance(i, list):
                                addDir(i[0].encode('utf-8'),i[1].encode('utf-8'),1,icon,FANART,'','','','','source')
                            else:
                                thumb = icon
                                fanart = FANART
                                desc = ''
                                date = ''
                                credits = ''
                                genre = ''
                                visible = 'true'
                                media_type = 'other'
                                if i.has_key('thumbnail'):
                                    thumb = i['thumbnail']
                                if i.has_key('fanart'):
                                    fanart = i['fanart']
                                if i.has_key('description'):
                                    desc = i['description']
                                if i.has_key('date'):
                                    date = i['date']
                                if i.has_key('genre'):
                                    genre = i['genre']
                                if i.has_key('credits'):
                                    credits = i['credits']
                                if i.has_key('visible'):
                                    visible = i['visible']
                                if i.has_key('media_type'):
                                    media_type = i['media_type']
                                
                                types_dict = {'ltv':'Live TV', 'vod':'Video on Demand', 'sport':'Sport', 'download':'Download', 'other':'Other'}

                                if selection == "all":
                                    try: type_media = types_dict[media_type]
                                    except: type_media = "Unknown"
                                    
                                    if visible != "true":
                                        addDir("[" + type_media + "] " +i['title'].encode('utf-8') + " - [I]Hidden Source[/I]",i['url'].encode('utf-8'),1,thumb,fanart,desc,genre,date,credits,'source')
                                    else:
                                        addDir("[" + type_media + "] " + i['title'].encode('utf-8') ,i['url'].encode('utf-8'),1,thumb,fanart,desc,genre,date,credits,'source')
                                if visible == "true":
                                    if media_type == selection:
                                        addDir(i['title'].encode('utf-8'),i['url'].encode('utf-8'),1,thumb,fanart,desc,genre,date,credits,'source')
                        except: traceback.print_exc()
                else:
                    if len(sources) == 1:
                        if isinstance(sources[0], list):
                            getData(sources[0][1].encode('utf-8'),FANART)
                        else:
                            getData(sources[0]['url'], sources[0]['fanart'])
        
            addDir('Remove sources by name','Remove Source',88,icon,FANART,'','','','')
        except: traceback.print_exc()

def addSourceFromAList(url=None, media_type=99):
        if addon.getSetting("user_agent") != "":
            if addon.getSetting("user_agent") != "Default":
                user_agent = addon.getSetting('user_agent').decode('utf-8')
            else:
                user_agent = None
        else:
            user_agent = None

        if url == '' or url is None:
            return

        source_urls = [line.rstrip('\n') for line in open(url, "r")]
        
        print url
        print source_urls

        names = ['Live TV', 'Video on Demand', 'Sport', 'Download File', 'Other']
        types = ['ltv', 'vod', 'sport', 'download', 'other']
        dialog = xbmcgui.Dialog()
        index = dialog.select('Select what your content has', names)
        if index >= 0:
            media_type = types[index]

        visible = addon.getSetting("new_source_as_visible")

        media_info = None
        #print 'source_url',source_url
        nameStr = ""
        keyboard = xbmc.Keyboard(nameStr,'Select your name, your sources will be added as SOURCE [#1, #2, #3, ...]')
        keyboard.doModal()
        if (keyboard.isConfirmed() == False):
            return
        newStr = keyboard.getText()
        if len(newStr) == 0:
            return
        i = 1
        for source_url in source_urls:
            addon_log('Adding New Source: '+source_url.encode('utf-8'))
            if user_agent:
                source_url = source_url + "|User-Agent=" + user_agent
            data = getSoup(source_url)
                    
            if isinstance(data,BeautifulSOAP):
                if data.find('channels_info'):
                    media_info = data.channels_info
                elif data.find('items_info'):
                    media_info = data.items_info
            if media_info:
                source_media = {}
                source_media['url'] = source_url
                source_media['visible'] = visible
                source_media['media_type'] = media_type
                try: 
                    source_media['title'] = media_info.title.string + " #" + str(i)
                    i = i + 1
                except: pass
                try: source_media['thumbnail'] = media_info.thumbnail.string
                except: pass
                try: source_media['fanart'] = media_info.fanart.string
                except: pass
                try: source_media['genre'] = media_info.genre.string
                except: pass
                try: source_media['description'] = media_info.description.string
                except: pass
                try: source_media['date'] = media_info.date.string
                except: pass
                try: source_media['credits'] = media_info.credits.string
                except: pass
            else:
                if addon.getSetting("new_file_source_thumb") != "" or addon.getSetting("new_url_source_thumb") != "":
                    if addon.getSetting("new_file_source_thumb") != "":
                        thumbnail = addon.getSetting("new_file_source_thumb")
                    else:
                        thumbnail = addon.getSetting("new_url_source_thumb")
                else: 
                    thumbnail = None
                
                if addon.getSetting("new_url_source_desc") != "":
                    description = addon.getSetting("new_file_source_thumb")
                else: 
                    description = None

                source_media = {}
                if addon.getSetting("new_source_name_bold") == "true":
                    source_media['title'] = "[B]" + newStr + "[/B]" + " #" + str(i)
                else:
                    source_media['title'] = newStr + " #" + str(i)
                i = i + 1
                source_media['url'] = source_url
                source_media['fanart'] = fanart
                source_media['visible'] = visible
                source_media['media_type'] = media_type
                if thumbnail is not None:
                    source_media['thumbnail'] = thumbnail
                if description is not None:
                    source_media['description'] = description

            if os.path.exists(source_file)==False:
                source_list = []
                source_list.append(source_media)
                b = open(source_file,"w")
                b.write(json.dumps(source_list))
                b.close()
            else:
                sources = json.loads(open(source_file,"r").read())
                sources.append(source_media)
                b = open(source_file,"w")
                b.write(json.dumps(sources))
                b.close()
            addon.setSetting('new_url_source', "")
            addon.setSetting('new_file_source', "")
            xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,New source added.,5000,"+icon+")")
            if not url is None:
                if 'xbmcplus.xb.funpic.de' in url:
                    xbmc.executebuiltin("XBMC.Container.Update(%s?mode=14,replace)" %sys.argv[0])
                elif 'community-links' in url:
                    xbmc.executebuiltin("XBMC.Container.Update(%s?mode=10,replace)" %sys.argv[0])
            else: addon.openSettings()
        xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,All sources has been added.,5000,"+icon+")")

def purgeLists():
    with open(source_file,"w") as f:
        f.write("[]")
    xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,All sources has been removed.,5000,"+icon+")")

def addSourceWizard():
    keyboard = xbmc.Keyboard("",'Insert URL')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    url = keyboard.getText()
    if len(url) == 0:
        return
    
    keyboard = xbmc.Keyboard("",'Insert User-Agent (Leave blank to use default)')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    ua = keyboard.getText()
    if len(ua) != 0:
        url = url + "|User-Agent=" + ua

    names = ['Live TV', 'Video on Demand', 'Sport', 'Download File', 'Other']
    types = ['ltv', 'vod', 'sport', 'download', 'other']
    dialog = xbmcgui.Dialog()
    index = dialog.select('Select source type', names)
    if index >= 0:
        media_type = types[index]

    addSource(url=url, media_type=media_type, wizard=True)
    

def addSource(url=None, media_type="other", wizard=False):
        if wizard is False:
            if addon.getSetting("user_agent") != "" and addon.getSetting("user_agent") != "Default":
                user_agent = addon.getSetting('user_agent').decode('utf-8')
            else:
                user_agent = False

            if url == '' or url is None:
                return
            
            if user_agent is not False:
                source_url = url + "|User-Agent=" + user_agent
        
            names = ['Live TV', 'Video on Demand', 'Sport', 'Download File', 'Other']
            types = ['ltv', 'vod', 'sport', 'download', 'other']
            dialog = xbmcgui.Dialog()
            index = dialog.select('Select source type', names)
            if index >= 0:
                media_type = types[index]
        else:
            source_url = url

        addon_log('Adding New Source: '+source_url.encode('utf-8'))
        visible = addon.getSetting("new_source_as_visible")
        media_info = None
        #print 'source_url',source_url
        data = getSoup(source_url)
                
        if isinstance(data,BeautifulSOAP):
            if data.find('channels_info'):
                media_info = data.channels_info
            elif data.find('items_info'):
                media_info = data.items_info
        if media_info:
            source_media = {}
            source_media['url'] = source_url
            source_media['visible'] = visible
            source_media['media_type'] = media_type
            try: source_media['title'] = media_info.title.string
            except: pass
            try: source_media['thumbnail'] = media_info.thumbnail.string
            except: pass
            try: source_media['fanart'] = media_info.fanart.string
            except: pass
            try: source_media['genre'] = media_info.genre.string
            except: pass
            try: source_media['description'] = media_info.description.string
            except: pass
            try: source_media['date'] = media_info.date.string
            except: pass
            try: source_media['credits'] = media_info.credits.string
            except: pass
        else:
            if '/' in source_url:
                nameStr = source_url.split('/')[-1].split('.')[0]
            if '\\' in source_url:
                nameStr = source_url.split('\\')[-1].split('.')[0]
            if '%' in nameStr:
                nameStr = urllib.unquote_plus(nameStr)
            keyboard = xbmc.Keyboard(nameStr,'Displayed Name, Rename?')
            keyboard.doModal()
            if (keyboard.isConfirmed() == False):
                return
            newStr = keyboard.getText()
            if len(newStr) == 0:
                return

            if addon.getSetting("new_file_source_thumb") != "" or addon.getSetting("new_url_source_thumb") != "":
                if addon.getSetting("new_file_source_thumb") != "":
                    thumbnail = addon.getSetting("new_file_source_thumb")
                else:
                    thumbnail = addon.getSetting("new_url_source_thumb")
            else: 
                thumbnail = None
            
            if addon.getSetting("new_url_source_desc") != "":
                description = addon.getSetting("new_file_source_thumb")
            else: 
                description = None

            source_media = {}
            if addon.getSetting("new_source_name_bold") == "true":
                source_media['title'] = "[B]" + newStr + "[/B]"
            else:
                source_media['title'] = newStr
            source_media['url'] = source_url
            source_media['fanart'] = fanart
            source_media['visible'] = visible
            source_media['media_type'] = media_type
            if thumbnail is not None:
                source_media['thumbnail'] = thumbnail
            if description is not None:
                source_media['description'] = description

        if os.path.exists(source_file)==False:
            source_list = []
            source_list.append(source_media)
            b = open(source_file,"w")
            b.write(json.dumps(source_list))
            b.close()
        else:
            sources = json.loads(open(source_file,"r").read())
            sources.append(source_media)
            b = open(source_file,"w")
            b.write(json.dumps(sources))
            b.close()
        addon.setSetting('new_url_source', "")
        addon.setSetting('new_file_source', "")
        xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,New source added.,5000,"+icon+")")
        if not url is None:
            if 'xbmcplus.xb.funpic.de' in url:
                xbmc.executebuiltin("XBMC.Container.Update(%s?mode=14,replace)" %sys.argv[0])
            elif 'community-links' in url:
                xbmc.executebuiltin("XBMC.Container.Update(%s?mode=10,replace)" %sys.argv[0])
        else: addon.openSettings()

def rmSource(name):
        sources = json.loads(open(source_file,"r").read())
        for index in range(len(sources)):
            if isinstance(sources[index], list):
                if sources[index][0] == name:
                    del sources[index]
                    b = open(source_file,"w")
                    b.write(json.dumps(sources))
                    b.close()
                    break
            else:
                if sources[index]['title'] == name:
                    del sources[index]
                    b = open(source_file,"w")
                    b.write(json.dumps(sources))
                    b.close()
                    break
        xbmc.executebuiltin("XBMC.Container.Refresh")

def rmSourceWithWizard():
    xbmcgui.Dialog().ok("Live Streams Pro", "Pay attention, sources are removed with flag 'like', if you type 'lsp' this will remove all sources with 'lsp' in name!") 
    keyboard = xbmc.Keyboard("",'Write name of source(s) you wanna remove')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    name = keyboard.getText()
    
    sources = json.loads(open(source_file,"r").read())
    for index in range(len(sources)):
        if isinstance(sources[index], list):
            if name in sources[index][0]:
                del sources[index]
        else:
            if name in sources[index]['title']:
                del sources[index]
    b = open(source_file,"w")
    b.write(json.dumps(sources))
    b.close()
    xbmc.executebuiltin("XBMC.Container.Refresh")  

def get_xml_database(url, browse=False):
        if url is None:
            url = 'http://xbmcplus.xb.funpic.de/www-data/filesystem/'
        soup = BeautifulSoup(makeRequest(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        for i in soup('a'):
            href = i['href']
            if not href.startswith('?'):
                name = i.string
                if name not in ['Parent Directory', 'recycle_bin/']:
                    if href.endswith('/'):
                        if browse:
                            addDir(name,url+href,15,icon,fanart,'','','')
                        else:
                            addDir(name,url+href,14,icon,fanart,'','','')
                    elif href.endswith('.xml'):
                        if browse:
                            addDir(name,url+href,1,icon,fanart,'','','','','download')
                        else:
                            if os.path.exists(source_file)==True:
                                if name in SOURCES:
                                    addDir(name+' (in use)',url+href,11,icon,fanart,'','','','','download')
                                else:
                                    addDir(name,url+href,11,icon,fanart,'','','','','download')
                            else:
                                addDir(name,url+href,11,icon,fanart,'','','','','download')

def getCommunitySources(browse=False):
        url = 'http://community-links.googlecode.com/svn/trunk/'
        soup = BeautifulSoup(makeRequest(url), convertEntities=BeautifulSoup.HTML_ENTITIES)
        files = soup('ul')[0]('li')[1:]
        for i in files:
            name = i('a')[0]['href']
            if browse:
                addDir(name,url+name,1,icon,fanart,'','','','','download')
            else:
                addDir(name,url+name,11,icon,fanart,'','','','','download')

def getSoup(url, data=None):
        global viewmode,tsdownloader, hlsretry
        tsdownloader=False
        hlsretry=False
        if addon.getSetting('tsdownloader') == 'true' :
            tsdownloader = True
        if addon.getSetting('hlsretry') == 'true' :
            hlsretry = True
        if url.startswith('http://') or url.startswith('https://'):
            enckey=False
            if '$$TSDOWNLOADER$$' in url:
                tsdownloader=True
                url=url.replace("$$TSDOWNLOADER$$","")
            if '$$HLSRETRY$$' in url:
                hlsretry=True
                url=url.replace("$$HLSRETRY$$","")
            if '$$LSProEncKey=' in url:
                enckey=url.split('$$LSProEncKey=')[1].split('$$')[0]
                rp='$$LSProEncKey=%s$$'%enckey
                url=url.replace(rp,"")
                
            data = makeRequest(url)
            if enckey:
                    import pyaes
                    enckey=enckey.encode("ascii")
                    print enckey
                    missingbytes=16-len(enckey)
                    enckey=enckey+(chr(0)*(missingbytes))
                    print repr(enckey)
                    data=base64.b64decode(data)
                    decryptor = pyaes.new(enckey , pyaes.MODE_ECB, IV=None)
                    data=decryptor.decrypt(data).split('\0')[0]
                    #print repr(data)
            if re.search("#EXTM3U",data) or 'm3u' in url:
                return data
        elif data == None:
            if not '/'  in url or not '\\' in url:
                url = os.path.join(communityfiles,url)
            if xbmcvfs.exists(url):
                if url.startswith("smb://") or url.startswith("nfs://"):
                    copy = xbmcvfs.copy(url, os.path.join(profile, 'temp', 'sorce_temp.txt'))
                    if copy:
                        data = open(os.path.join(profile, 'temp', 'sorce_temp.txt'), "r").read()
                        xbmcvfs.delete(os.path.join(profile, 'temp', 'sorce_temp.txt'))
                    else:
                        addon_log("failed to copy from smb:")
                else:
                    data = open(url, 'r').read()
                    if re.match("#EXTM3U",data)or 'm3u' in url:
                        return data
            else:
                addon_log("Soup Data not found!")
                return
        if '<SetViewMode>' in data:
            try:
                viewmode=re.findall('<SetViewMode>(.*?)<',data)[0]
                xbmc.executebuiltin("Container.SetViewMode(%s)"%viewmode)
                print 'done setview',viewmode
            except: pass
        return BeautifulSOAP(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)

def processPyFunction(data):
    try:
        if data and len(data)>0 and data.startswith('$pyFunction:'):
            data=doEval(data.split('$pyFunction:')[1],'',None,None )
    except: pass

    return data

def getData(url, fanart, data=None):

    soup = getSoup(url,data)
    #print type(soup)
    if isinstance(soup,BeautifulSOAP):
    #print 'xxxxxxxxxxsoup',soup
        if len(soup('channels')) > 0 and addon.getSetting('donotshowbychannels') == 'false':
            channels = soup('channel')
            for channel in channels:

                linkedUrl=''
                lcount=0
                try:
                    linkedUrl =  channel('externallink')[0].string
                    lcount=len(channel('externallink'))
                except: pass
                #print 'linkedUrl',linkedUrl,lcount
                if lcount>1: linkedUrl=''

                name = channel('name')[0].string
                try:
                    name=processPyFunction(name)
                except: pass                
                thumbnail = channel('thumbnail')[0].string
                if thumbnail == None:
                    thumbnail = ''
                thumbnail=processPyFunction(thumbnail)
                try:
                    if not channel('fanart'):
                        if addon.getSetting('use_thumb') == "true":
                            fanArt = thumbnail
                        else:
                            fanArt = fanart
                    else:
                        fanArt = channel('fanart')[0].string
                    if fanArt == None:
                        raise
                except:
                    fanArt = fanart

                try:
                    desc = channel('info')[0].string
                    if desc == None:
                        raise
                except:
                    desc = ''

                try:
                    genre = channel('genre')[0].string
                    if genre == None:
                        raise
                except:
                    genre = ''

                try:
                    date = channel('date')[0].string
                    if date == None:
                        raise
                except:
                    date = ''

                try:
                    credits = channel('credits')[0].string
                    if credits == None:
                        raise
                except:
                    credits = ''

                try:
                    if linkedUrl=='':
                        addDir(name.encode('utf-8', 'ignore'),url.encode('utf-8'),2,thumbnail,fanArt,desc,genre,date,credits,True)
                    else:
                        #print linkedUrl
                        addDir(name.encode('utf-8'),linkedUrl.encode('utf-8'),1,thumbnail,fanArt,desc,genre,date,None,'source')
                except:
                    addon_log('There was a problem adding directory from getData(): '+name.encode('utf-8', 'ignore'))
        else:
            addon_log('No Channels: getItems')
            getItems(soup('item'),fanart)
    else:
        parse_m3u(soup)

# borrow from https://github.com/enen92/P2P-Streams-XBMC/blob/master/plugin.video.p2p-streams/resources/core/livestreams.py
# This will not go through the getItems functions ( means you must have ready to play url, no regex)
def parse_m3u(data):
    content = data.rstrip()
    match = re.compile(r'#EXTINF:(.+?),(.*?)[\n\r]+([^\r\n]+)').findall(content)
    total = len(match)
    print 'tsdownloader',tsdownloader
    DESCRIPTION_CHANNEL = ""

    if addon.getSetting("epg_enable") == "true" and addon.getSetting("epg_link") != "":
        try:
            EPG = open(os.path.join(profile, "epg.xml")).read()
        except:
            EPG = False
    else:
        EPG = False

    for other,channel_name,stream_url in match:
        if EPG is not False:
            from datetime import datetime
            today = datetime.utcnow().strftime('%Y%m%d')
            now = datetime.utcnow().strftime('%Y%m%d%H%M') + "00"
            pattern = r'start="([0-9 \+]*)" stop="([0-9 \+]*)" channel="'+ channel_name + r'">[\n\r ]+<title lang="it">(.+?)<\/title>[\n\r ]+<desc lang="it">(.+?)<\/desc>'
            epgs_channel = re.compile(pattern, re.MULTILINE | re.DOTALL).findall(EPG)

            for start, stop, title, desc in epgs_channel:
                start = int(start.split(" ")[0])
                stop = int(stop[0].split(" ")[0])
                if int(now) > start and int(now) < stop:
                    # Current element is the element
                    DESCRIPTION_CHANNEL = title + "\n" + desc + "\n" + str(start) + " " + str(stop)
                    break

        if 'tvg-logo' in other:
            thumbnail = re_me(other,'tvg-logo=[\'"](.*?)[\'"]')
            if thumbnail:
                if thumbnail.startswith('http'):
                    thumbnail = thumbnail
                else:
                    thumbnail = thumbnail
        elif addon.getSetting("logo_epg_enable") == "true" and addon.getSetting('logo-folderPath') != "":
            logo_url = addon.getSetting('logo-folderPath')
            thumbnail = logo_url + channel_name + ".png"
        else:
            thumbnail = ''
        
        if 'type' in other:
            mode_type = re_me(other,'type=[\'"](.*?)[\'"]')
            if mode_type == 'yt-dl':
                stream_url = stream_url +"&mode=18"
            elif mode_type == 'regex':
                url = stream_url.split('&regexs=')
                #print url[0] getSoup(url,data=None)
                regexs = parse_regex(getSoup('', data=url[1]))

                addLink(url[0], channel_name,thumbnail,'','','','','',None,regexs,total)
                continue
            elif mode_type == 'ftv':
                stream_url = 'plugin://plugin.video.F.T.V/?name='+urllib.quote(channel_name) +'&url=' +stream_url +'&mode=125&ch_fanart=na'
        #elif tsdownloader and '.ts' in stream_url:
        elif '.ts' in stream_url:
            stream_url = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(stream_url)+'&amp;streamtype=TSDOWNLOADER&amp;name='+urllib.quote(channel_name)
        #elif hlsretry and '.m3u8' in stream_url:
        elif '.m3u8' in stream_url:
            stream_url = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(stream_url)+'&amp;streamtype=HLSRETRY&amp;name='+urllib.quote(channel_name)
        elif addon.getSetting("force_proxy") == "true":
            stream_url = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(stream_url)+'&amp;name='+urllib.quote(channel_name)
        addLink(stream_url, channel_name,thumbnail,'',DESCRIPTION_CHANNEL,'','','',None,'',total)

def getChannelItems(name,url,fanart):
        soup = getSoup(url)
        channel_list = soup.find('channel', attrs={'name' : name.decode('utf-8')})
        items = channel_list('item')
        try:
            fanArt = channel_list('fanart')[0].string
            if fanArt == None:
                raise
        except:
            fanArt = fanart
        for channel in channel_list('subchannel'):
            name = channel('name')[0].string
            try:
                name=processPyFunction(name)
            except: pass
            try:
                thumbnail = channel('thumbnail')[0].string
                if thumbnail == None:
                    raise
                thumbnail=processPyFunction(thumbnail)
            except:
                thumbnail = ''
            try:
                if not channel('fanart'):
                    if addon.getSetting('use_thumb') == "true":
                        fanArt = thumbnail
                else:
                    fanArt = channel('fanart')[0].string
                if fanArt == None:
                    raise
            except:
                pass
            try:
                desc = channel('info')[0].string
                if desc == None:
                    raise
            except:
                desc = ''

            try:
                genre = channel('genre')[0].string
                if genre == None:
                    raise
            except:
                genre = ''

            try:
                date = channel('date')[0].string
                if date == None:
                    raise
            except:
                date = ''

            try:
                credits = channel('credits')[0].string
                if credits == None:
                    raise
            except:
                credits = ''

            try:
                addDir(name.encode('utf-8', 'ignore'),url.encode('utf-8'),3,thumbnail,fanArt,desc,genre,credits,date)
            except:
                addon_log('There was a problem adding directory - '+name.encode('utf-8', 'ignore'))
        getItems(items,fanArt)

def getSubChannelItems(name,url,fanart):
        soup = getSoup(url)
        channel_list = soup.find('subchannel', attrs={'name' : name.decode('utf-8')})
        items = channel_list('subitem')
        getItems(items,fanart)

def getItems(items,fanart,dontLink=False):
        total = len(items)
        addon_log('Total Items: %s' %total)
        add_playlist = addon.getSetting('add_playlist')
        ask_playlist_items =addon.getSetting('ask_playlist_items')
        use_thumb = addon.getSetting('use_thumb')
        parentalblock =addon.getSetting('parentalblocked')
        parentalblock= parentalblock=="true"
        for item in items:
            isXMLSource=False
            isJsonrpc = False
            
            applyblock='false'
            try:
                applyblock = item('parentalblock')[0].string
            except:
                addon_log('parentalblock Error')
                applyblock = ''
            if applyblock=='true' and parentalblock: continue
                
            try:
                name = item('title')[0].string
                if name is None:
                    name = 'unknown?'
                try:
                    name=processPyFunction(name)
                except: pass
                
            except:
                addon_log('Name Error')
                name = ''


            try:
                if item('epg'):
                    if item.epg_url:
                        addon_log('Get EPG Regex')
                        epg_url = item.epg_url.string
                        epg_regex = item.epg_regex.string
                        epg_name = get_epg(epg_url, epg_regex)
                        if epg_name:
                            name += ' - ' + epg_name
                    elif item('epg')[0].string > 1:
                        name += getepg(item('epg')[0].string)
                else:
                    pass
            except:
                addon_log('EPG Error')
            try:
                url = []
                if len(item('link')) >0:
                    #print 'item link', item('link')

                    for i in item('link'):
                        if not i.string == None:
                            url.append(i.string)

                elif len(item('sportsdevil')) >0:
                    for i in item('sportsdevil'):
                        if not i.string == None:
                            sportsdevil = 'plugin://plugin.video.SportsDevil/?mode=1&amp;item=catcher%3dstreams%26url=' +i.string
                            referer = item('referer')[0].string
                            if referer:
                                #print 'referer found'
                                sportsdevil = sportsdevil + '%26referer=' +referer
                            url.append(sportsdevil)
                elif len(item('p2p')) >0:
                    for i in item('p2p'):
                        if not i.string == None:
                            if 'sop://' in i.string:
                                sop = 'plugin://plugin.video.p2p-streams/?mode=2url='+i.string +'&' + 'name='+name
                                url.append(sop)
                            else:
                                p2p='plugin://plugin.video.p2p-streams/?mode=1&url='+i.string +'&' + 'name='+name
                                url.append(p2p)
                elif len(item('vaughn')) >0:
                    for i in item('vaughn'):
                        if not i.string == None:
                            vaughn = 'plugin://plugin.stream.vaughnlive.tv/?mode=PlayLiveStream&amp;channel='+i.string
                            url.append(vaughn)
                elif len(item('ilive')) >0:
                    for i in item('ilive'):
                        if not i.string == None:
                            if not 'http' in i.string:
                                ilive = 'plugin://plugin.video.tbh.ilive/?url=http://www.streamlive.to/view/'+i.string+'&amp;link=99&amp;mode=iLivePlay'
                            else:
                                ilive = 'plugin://plugin.video.tbh.ilive/?url='+i.string+'&amp;link=99&amp;mode=iLivePlay'
                elif len(item('yt-dl')) >0:
                    for i in item('yt-dl'):
                        if not i.string == None:
                            ytdl = i.string + '&mode=18'
                            url.append(ytdl)
                elif len(item('dm')) >0:
                    for i in item('dm'):
                        if not i.string == None:
                            dm = "plugin://plugin.video.dailymotion_com/?mode=playVideo&url=" + i.string
                            url.append(dm)
                elif len(item('dmlive')) >0:
                    for i in item('dmlive'):
                        if not i.string == None:
                            dm = "plugin://plugin.video.dailymotion_com/?mode=playLiveVideo&url=" + i.string
                            url.append(dm)
                elif len(item('utube')) >0:
                    for i in item('utube'):
                        if not i.string == None:
                            if ' ' in i.string :
                                utube = 'plugin://plugin.video.youtube/search/?q='+ urllib.quote_plus(i.string)
                                isJsonrpc=utube
                            elif len(i.string) == 11:
                                utube = 'plugin://plugin.video.youtube/play/?video_id='+ i.string
                            elif (i.string.startswith('PL') and not '&order=' in i.string) or i.string.startswith('UU'):
                                utube = 'plugin://plugin.video.youtube/play/?&order=default&playlist_id=' + i.string
                            elif i.string.startswith('PL') or i.string.startswith('UU'):
                                utube = 'plugin://plugin.video.youtube/play/?playlist_id=' + i.string
                            elif i.string.startswith('UC') and len(i.string) > 12:
                                utube = 'plugin://plugin.video.youtube/channel/' + i.string + '/'
                                isJsonrpc=utube
                            elif not i.string.startswith('UC') and not (i.string.startswith('PL'))  :
                                utube = 'plugin://plugin.video.youtube/user/' + i.string + '/'
                                isJsonrpc=utube
                        url.append(utube)
                elif len(item('imdb')) >0:
                    for i in item('imdb'):
                        if not i.string == None:
                            if addon.getSetting('genesisorpulsar') == '0':
                                imdb = 'plugin://plugin.video.genesis/?action=play&imdb='+i.string
                            else:
                                imdb = 'plugin://plugin.video.pulsar/movie/tt'+i.string+'/play'
                            url.append(imdb)

                elif len(item('f4m')) >0:
                    for i in item('f4m'):
                        if not i.string == None:
                            if '.f4m' in i.string:
                                f4m = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(i.string)
                            elif '.m3u8' in i.string:
                                f4m = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(i.string)+'&amp;streamtype=HLS'

                            else:
                                f4m = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(i.string)+'&amp;streamtype=SIMPLE'
                        url.append(f4m)       
                
                elif len(item('ftv')) >0:
                    for i in item('ftv'):
                        if not i.string == None:
                            ftv = 'plugin://plugin.video.F.T.V/?name='+urllib.quote(name) +'&url=' +i.string +'&mode=125&ch_fanart=na'
                        url.append(ftv)
                elif len(item('urlsolve')) >0:                    
                    for i in item('urlsolve'):
                        if not i.string == None:
                            resolver = i.string +'&mode=19'
                            url.append(resolver)
                elif len(item('inputstream')) >0:                    
                    for i in item('inputstream'):
                        if not i.string == None:
                            istream = i.string +'&mode=20'
                            url.append(istream)
                elif len(item('slproxy')) >0:
                    for i in item('slproxy'):
                        if not i.string == None:
                            istream = i.string +'&mode=22'
                            url.append(istream)       

                if len(url) < 1:
                    raise

            except:
                addon_log('Error <link> element, Passing:'+name.encode('utf-8', 'ignore'))
                continue
            try:
                isXMLSource = item('externallink')[0].string
            except: pass

            if isXMLSource:
                ext_url=[isXMLSource]
                isXMLSource=True
            else:
                isXMLSource=False
            try:
                isJsonrpc = item('jsonrpc')[0].string
            except: pass
            if isJsonrpc:

                ext_url=[isJsonrpc]
                #print 'JSON-RPC ext_url',ext_url
                isJsonrpc=True
            else:
                isJsonrpc=False
            try:
                thumbnail = item('thumbnail')[0].string
                if thumbnail == None:
                    raise
                thumbnail=processPyFunction(thumbnail)
            except:
                thumbnail = ''
            try:
                if not item('fanart'):
                    if addon.getSetting('use_thumb') == "true":
                        fanArt = thumbnail
                    else:
                        fanArt = fanart
                else:
                    fanArt = item('fanart')[0].string
                if fanArt == None:
                    raise
            except:
                fanArt = fanart
            try:
                desc = item('info')[0].string
                if desc == None:
                    raise
            except:
                desc = ''

            try:
                genre = item('genre')[0].string
                if genre == None:
                    raise
            except:
                genre = ''

            try:
                date = item('date')[0].string
                if date == None:
                    raise
            except:
                date = ''

            regexs = None
            if item('regex'):
                try:
                    reg_item = item('regex')
                    regexs = parse_regex(reg_item)
                except:
                    pass
            try:
                
                if len(url) > 1:
                    alt = 0
                    playlist = []
                    ignorelistsetting=True if '$$LSPlayOnlyOne$$' in url[0] else False
                    
                    for i in url:
                            if  add_playlist == "false" and not ignorelistsetting:
                                alt += 1
                                addLink(i,'%s) %s' %(alt, name.encode('utf-8', 'ignore')),thumbnail,fanArt,desc,genre,date,True,playlist,regexs,total)
                            elif  (add_playlist == "true" and  ask_playlist_items == 'true') or ignorelistsetting:
                                if regexs:
                                    playlist.append(i+'&regexs='+regexs)
                                elif  any(x in i for x in resolve_url) and  i.startswith('http'):
                                    playlist.append(i+'&mode=19')
                                else:
                                    playlist.append(i)
                            else:
                                playlist.append(i)
                    
                    if len(playlist) > 1:                        
                        addLink('', name.encode('utf-8'),thumbnail,fanArt,desc,genre,date,True,playlist,regexs,total)
                else:
                    
                    if dontLink:
                        return name,url[0],regexs
                    if isXMLSource:
                            if not regexs == None: #<externallink> and <regex>
                                addDir(name.encode('utf-8'),ext_url[0].encode('utf-8'),1,thumbnail,fanArt,desc,genre,date,None,'!!update',regexs,url[0].encode('utf-8'))
                                #addLink(url[0],name.encode('utf-8', 'ignore')+  '[COLOR yellow]build XML[/COLOR]',thumbnail,fanArt,desc,genre,date,True,None,regexs,total)
                            else:
                                addDir(name.encode('utf-8'),ext_url[0].encode('utf-8'),1,thumbnail,fanArt,desc,genre,date,None,'source',None,None)
                                #addDir(name.encode('utf-8'),url[0].encode('utf-8'),1,thumbnail,fanart,desc,genre,date,None,'source')
                    elif isJsonrpc:
                        addDir(name.encode('utf-8'),ext_url[0],53,thumbnail,fanArt,desc,genre,date,None,'source')
                        #xbmc.executebuiltin("Container.SetViewMode(500)")
                    else:
                        try:
                            if '$doregex' in name and not getRegexParsed==None:
                                
                                tname,setres=getRegexParsed(regexs, name)
                                
                                if not tname==None:
                                    name=tname
                        except: pass
                        try:
                            if '$doregex' in thumbnail and not getRegexParsed==None:
                                tname,setres=getRegexParsed(regexs, thumbnail)
                                if not tname==None:
                                    thumbnail=tname
                        except: pass
                        addLink(url[0],name.encode('utf-8', 'ignore'),thumbnail,fanArt,desc,genre,date,True,None,regexs,total)
                    #print 'success'
            except:
                addon_log('There was a problem adding item - '+name.encode('utf-8', 'ignore'))

def parse_regex(reg_item):
                try:
                    regexs = {}
                    for i in reg_item:
                        regexs[i('name')[0].string] = {}
                        regexs[i('name')[0].string]['name']=i('name')[0].string
                        #regexs[i('name')[0].string]['expres'] = i('expres')[0].string
                        try:
                            regexs[i('name')[0].string]['expres'] = i('expres')[0].string
                            if not regexs[i('name')[0].string]['expres']:
                                regexs[i('name')[0].string]['expres']=''
                        except:
                            addon_log("Regex: -- No Referer --")
                        regexs[i('name')[0].string]['page'] = i('page')[0].string
                        try:
                            regexs[i('name')[0].string]['referer'] = i('referer')[0].string
                        except:
                            addon_log("Regex: -- No Referer --")
                        try:
                            regexs[i('name')[0].string]['connection'] = i('connection')[0].string
                        except:
                            addon_log("Regex: -- No connection --")

                        try:
                            regexs[i('name')[0].string]['notplayable'] = i('notplayable')[0].string
                        except:
                            addon_log("Regex: -- No notplayable --")

                        try:
                            regexs[i('name')[0].string]['noredirect'] = i('noredirect')[0].string
                        except:
                            addon_log("Regex: -- No noredirect --")
                        try:
                            regexs[i('name')[0].string]['origin'] = i('origin')[0].string
                        except:
                            addon_log("Regex: -- No origin --")
                        try:
                            regexs[i('name')[0].string]['accept'] = i('accept')[0].string
                        except:
                            addon_log("Regex: -- No accept --")
                        try:
                            regexs[i('name')[0].string]['includeheaders'] = i('includeheaders')[0].string
                        except:
                            addon_log("Regex: -- No includeheaders --")

                            
                        try:
                            regexs[i('name')[0].string]['listrepeat'] = i('listrepeat')[0].string
                        except:
                            addon_log("Regex: -- No listrepeat --")
                    
                            

                        try:
                            regexs[i('name')[0].string]['proxy'] = i('proxy')[0].string
                        except:
                            addon_log("Regex: -- No proxy --")
                            
                        try:
                            regexs[i('name')[0].string]['x-req'] = i('x-req')[0].string
                        except:
                            addon_log("Regex: -- No x-req --")

                        try:
                            regexs[i('name')[0].string]['x-addr'] = i('x-addr')[0].string
                        except:
                            addon_log("Regex: -- No x-addr --")                            
                            
                        try:
                            regexs[i('name')[0].string]['x-forward'] = i('x-forward')[0].string
                        except:
                            addon_log("Regex: -- No x-forward --")

                        try:
                            regexs[i('name')[0].string]['agent'] = i('agent')[0].string
                        except:
                            addon_log("Regex: -- No User Agent --")
                        try:
                            regexs[i('name')[0].string]['post'] = i('post')[0].string
                        except:
                            addon_log("Regex: -- Not a post")
                        try:
                            regexs[i('name')[0].string]['rawpost'] = i('rawpost')[0].string
                        except:
                            addon_log("Regex: -- Not a rawpost")
                        try:
                            regexs[i('name')[0].string]['htmlunescape'] = i('htmlunescape')[0].string
                        except:
                            addon_log("Regex: -- Not a htmlunescape")


                        try:
                            regexs[i('name')[0].string]['readcookieonly'] = i('readcookieonly')[0].string
                        except:
                            addon_log("Regex: -- Not a readCookieOnly")
                        #print i
                        try:
                            regexs[i('name')[0].string]['cookiejar'] = i('cookiejar')[0].string
                            if not regexs[i('name')[0].string]['cookiejar']:
                                regexs[i('name')[0].string]['cookiejar']=''
                        except:
                            addon_log("Regex: -- Not a cookieJar")
                        try:
                            regexs[i('name')[0].string]['setcookie'] = i('setcookie')[0].string
                        except:
                            addon_log("Regex: -- Not a setcookie")
                        try:
                            regexs[i('name')[0].string]['appendcookie'] = i('appendcookie')[0].string
                        except:
                            addon_log("Regex: -- Not a appendcookie")

                        try:
                            regexs[i('name')[0].string]['ignorecache'] = i('ignorecache')[0].string
                        except:
                            addon_log("Regex: -- no ignorecache")
                        #try:
                        #    regexs[i('name')[0].string]['ignorecache'] = i('ignorecache')[0].string
                        #except:
                        #    addon_log("Regex: -- no ignorecache")

                    regexs = urllib.quote(repr(regexs))
                    return regexs
                    #print regexs
                except:
                    regexs = None
                    addon_log('regex Error: '+name.encode('utf-8', 'ignore'))
#copies from lamda's implementation
def get_ustream(url):
    try:
        for i in range(1, 51):
            result = getUrl(url)
            if "EXT-X-STREAM-INF" in result: return url
            if not "EXTM3U" in result: return
            xbmc.sleep(2000)
        return
    except:
        return

def getRegexParsed(regexs, url,cookieJar=None,forCookieJarOnly=False,recursiveCall=False,cachedPages={}, rawPost=False, cookie_jar_file=None):#0,1,2 = URL, regexOnly, CookieJarOnly
        if not recursiveCall:
            regexs = eval(urllib.unquote(regexs))
        #cachedPages = {}
        #print 'url',url
        doRegexs = re.compile('\$doregex\[([^\]]*)\]').findall(url)
        setresolved=True
        for k in doRegexs:
            if k in regexs:
                #print 'processing ' ,k
                m = regexs[k]
                #print m
                cookieJarParam=False
                if  'cookiejar' in m: # so either create or reuse existing jar
                    #print 'cookiejar exists',m['cookiejar']
                    cookieJarParam=m['cookiejar']
                    if  '$doregex' in cookieJarParam:
                        cookieJar=getRegexParsed(regexs, m['cookiejar'],cookieJar,True, True,cachedPages)
                        
                        cookieJarParam=True
                    else:
                        cookieJarParam=True
                #print 'm[cookiejar]',m['cookiejar'],cookieJar
                if cookieJarParam:
                    if cookieJar==None:
                        #print 'create cookie jar'
                        cookie_jar_file=None
                        if 'open[' in m['cookiejar']:
                            cookie_jar_file=m['cookiejar'].split('open[')[1].split(']')[0]
                        cookieJar=getCookieJar(cookie_jar_file)
                        if cookie_jar_file:
                            saveCookieJar(cookieJar,cookie_jar_file)
                        #import cookielib
                        #cookieJar = cookielib.LWPCookieJar()
                        #print 'cookieJar new',cookieJar
                    elif 'save[' in m['cookiejar']:
                        cookie_jar_file=m['cookiejar'].split('save[')[1].split(']')[0]
                        complete_path=os.path.join(profile,cookie_jar_file)
                        saveCookieJar(cookieJar,cookie_jar_file)
                if  m['page'] and '$doregex' in m['page']:
                    pg=getRegexParsed(regexs, m['page'],cookieJar,recursiveCall=True,cachedPages=cachedPages)
                    if len(pg)==0:
                        pg='http://regexfailed'
                    m['page']=pg

                if 'setcookie' in m and m['setcookie'] and '$doregex' in m['setcookie']:
                    m['setcookie']=getRegexParsed(regexs, m['setcookie'],cookieJar,recursiveCall=True,cachedPages=cachedPages)
                if 'appendcookie' in m and m['appendcookie'] and '$doregex' in m['appendcookie']:
                    m['appendcookie']=getRegexParsed(regexs, m['appendcookie'],cookieJar,recursiveCall=True,cachedPages=cachedPages)


                if  'post' in m and '$doregex' in m['post']:
                    m['post']=getRegexParsed(regexs, m['post'],cookieJar,recursiveCall=True,cachedPages=cachedPages)

                if  'rawpost' in m and '$doregex' in m['rawpost']:
                    m['rawpost']=getRegexParsed(regexs, m['rawpost'],cookieJar,recursiveCall=True,cachedPages=cachedPages,rawPost=True)
                    #print 'rawpost is now',m['rawpost']

                if 'rawpost' in m and '$epoctime$' in m['rawpost']:
                    m['rawpost']=m['rawpost'].replace('$epoctime$',getEpocTime())

                if 'rawpost' in m and '$epoctime2$' in m['rawpost']:
                    m['rawpost']=m['rawpost'].replace('$epoctime2$',getEpocTime2())


                link=''
                if m['page'] and m['page'] in cachedPages and not 'ignorecache' in m and forCookieJarOnly==False :
                    #print 'using cache page',m['page']
                    link = cachedPages[m['page']]
                else:
                    if m['page'] and  not m['page']=='' and  m['page'].startswith('http'):
                        if '$epoctime$' in m['page']:
                            m['page']=m['page'].replace('$epoctime$',getEpocTime())
                        if '$epoctime2$' in m['page']:
                            m['page']=m['page'].replace('$epoctime2$',getEpocTime2())

                        #print 'Ingoring Cache',m['page']
                        page_split=m['page'].split('|')
                        pageUrl=page_split[0]
                        header_in_page=None
                        if len(page_split)>1:
                            header_in_page=page_split[1]
                        current_proxies=urllib2.ProxyHandler(urllib2.getproxies())
        
        
                        #print 'getting pageUrl',pageUrl
                        req = urllib2.Request(pageUrl)
                        if 'proxy' in m:
                            proxytouse= m['proxy']
                            if pageUrl[:5]=="https":
                                proxy = urllib2.ProxyHandler({ 'https' : proxytouse})
                                #req.set_proxy(proxytouse, 'https')
                            else:
                                proxy = urllib2.ProxyHandler({ 'http'  : proxytouse})
                                #req.set_proxy(proxytouse, 'http')
                            opener = urllib2.build_opener(proxy)
                            urllib2.install_opener(opener)
                            
                        
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
                        proxytouse=None

                        if 'referer' in m:
                            req.add_header('Referer', m['referer'])
                        if 'accept' in m:
                            req.add_header('Accept', m['accept'])
                        if 'agent' in m:
                            req.add_header('User-agent', m['agent'])
                        if 'x-req' in m:
                            req.add_header('X-Requested-With', m['x-req'])
                        if 'x-addr' in m:
                            req.add_header('x-addr', m['x-addr'])
                        if 'x-forward' in m:
                            req.add_header('X-Forwarded-For', m['x-forward'])
                        if 'setcookie' in m:
                            req.add_header('Cookie', m['setcookie'])
                        if 'appendcookie' in m:
                            cookiestoApend=m['appendcookie']
                            cookiestoApend=cookiestoApend.split(';')
                            for h in cookiestoApend:
                                n,v=h.split('=')
                                w,n= n.split(':')
                                ck = cookielib.Cookie(version=0, name=n, value=v, port=None, port_specified=False, domain=w, domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
                                cookieJar.set_cookie(ck)
                        if 'origin' in m:
                            req.add_header('Origin', m['origin'])
                        if header_in_page:
                            header_in_page=header_in_page.split('&')
                            for h in header_in_page:
                                if h.split('=')==2:
                                    n,v=h.split('=')
                                else:
                                    vals=h.split('=')
                                    n=vals[0]
                                    v='='.join(vals[1:])
                                #n,v=h.split('=')
                                req.add_header(n,v)
                        
                        if not cookieJar==None:
                            cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
                            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
                            opener = urllib2.install_opener(opener)
                            
                            if 'noredirect' in m:
                                opener = urllib2.build_opener(cookie_handler,NoRedirection, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
                                opener = urllib2.install_opener(opener)
                        elif 'noredirect' in m:
                            opener = urllib2.build_opener(NoRedirection, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
                            opener = urllib2.install_opener(opener)
                            

                        if 'connection' in m:
                            from keepalive import HTTPHandler
                            keepalive_handler = HTTPHandler()
                            opener = urllib2.build_opener(keepalive_handler)
                            urllib2.install_opener(opener)


                        #print 'after cookie jar'
                        post=None

                        if 'post' in m:
                            postData=m['post']
                            #if '$LiveStreamRecaptcha' in postData:
                            #    (captcha_challenge,catpcha_word,idfield)=processRecaptcha(m['page'],cookieJar)
                            #    if captcha_challenge:
                            #        postData=postData.replace('$LiveStreamRecaptcha','manual_recaptcha_challenge_field:'+captcha_challenge+',recaptcha_response_field:'+catpcha_word+',id:'+idfield)
                            splitpost=postData.split(',')
                            post={}
                            for p in splitpost:
                                n=p.split(':')[0]
                                v=p.split(':')[1]
                                post[n]=v
                            post = urllib.urlencode(post)

                        if 'rawpost' in m:
                            post=m['rawpost']
                            #if '$LiveStreamRecaptcha' in post:
                            #    (captcha_challenge,catpcha_word,idfield)=processRecaptcha(m['page'],cookieJar)
                            #    if captcha_challenge:
                            #       post=post.replace('$LiveStreamRecaptcha','&manual_recaptcha_challenge_field='+captcha_challenge+'&recaptcha_response_field='+catpcha_word+'&id='+idfield)
                        link=''
                        try:
                            
                            if post:
                                response = urllib2.urlopen(req,post)
                            else:
                                response = urllib2.urlopen(req)
                            if response.info().get('Content-Encoding') == 'gzip':
                                from StringIO import StringIO
                                import gzip
                                buf = StringIO( response.read())
                                f = gzip.GzipFile(fileobj=buf)
                                link = f.read()
                            else:
                                link=response.read()
                            
                        
                        
                            if 'proxy' in m and not current_proxies is None:
                                urllib2.install_opener(urllib2.build_opener(current_proxies))
                            
                            link=javascriptUnEscape(link)
                            #print repr(link)
                            #print link This just print whole webpage in LOG
                            if 'includeheaders' in m:
                                #link+=str(response.headers.get('Set-Cookie'))
                                link+='$$HEADERS_START$$:'
                                for b in response.headers:
                                    link+= b+':'+response.headers.get(b)+'\n'
                                link+='$$HEADERS_END$$:'
                            addon_log(link)
                            addon_log(cookieJar )

                            response.close()
                        except: 
                            pass
                        cachedPages[m['page']] = link
                        #print link
                        #print 'store link for',m['page'],forCookieJarOnly

                        if forCookieJarOnly:
                            return cookieJar# do nothing
                    elif m['page'] and  not m['page'].startswith('http'):
                        if m['page'].startswith('$pyFunction:'):
                            val=doEval(m['page'].split('$pyFunction:')[1],'',cookieJar,m )
                            if forCookieJarOnly:
                                return cookieJar# do nothing
                            link=val
                            link=javascriptUnEscape(link)
                        else:
                            link=m['page']
                if '$pyFunction:playmedia(' in m['expres'] or 'ActivateWindow'  in m['expres'] or 'RunPlugin'  in m['expres']  or '$PLAYERPROXY$=' in url  or  any(x in url for x in g_ignoreSetResolved):
                    setresolved=False
                if  '$doregex' in m['expres']:
                    m['expres']=getRegexParsed(regexs, m['expres'],cookieJar,recursiveCall=True,cachedPages=cachedPages)
                  
                if not m['expres']=='':
                    #print 'doing it ',m['expres']
                    if '$LiveStreamCaptcha' in m['expres']:
                        val=askCaptcha(m,link,cookieJar)
                        #print 'url and val',url,val
                        url = url.replace("$doregex[" + k + "]", val)

                    elif m['expres'].startswith('$pyFunction:') or '#$pyFunction' in m['expres']:
                        #print 'expeeeeeeeeeeeeeeeeeee',m['expres']
                        val=''
                        if m['expres'].startswith('$pyFunction:'):
                            val=doEval(m['expres'].split('$pyFunction:')[1],link,cookieJar,m)
                        else:
                            val=doEvalFunction(m['expres'],link,cookieJar,m)
                        if 'ActivateWindow' in m['expres'] or 'RunPlugin' in m['expres']  : return '',False
                        if forCookieJarOnly:
                            return cookieJar# do nothing
                        if 'listrepeat' in m:
                            listrepeat=m['listrepeat']                            
                            #ret=re.findall(m['expres'],link)
                            #print 'ret',val
                            return listrepeat,eval(val), m,regexs,cookieJar
                        #print 'repr',repr(val)
                        
                        try:
                            url = url.replace(u"$doregex[" + k + "]", val)
                        except: url = url.replace("$doregex[" + k + "]", val.decode("utf-8"))
                    else:
                        if 'listrepeat' in m:
                            listrepeat=m['listrepeat']
                            #print 'listrepeat',m['expres']
                            #print m['expres']
                            #print 'aaaa'
                            #print link
                            ret=re.findall(m['expres'],link)
                            #print 'ret',ret
                            return listrepeat,ret, m,regexs,cookieJar
                             
                        val=''
                        if not link=='':
                            #print 'link',link
                            reg = re.compile(m['expres']).search(link)                            
                            try:
                                val=reg.group(1).strip()
                            except: traceback.print_exc()
                        elif m['page']=='' or m['page']==None:
                            val=m['expres']
                            
                        if rawPost:
                            val=urllib.quote_plus(val)
                        if 'htmlunescape' in m:
                            #val=urllib.unquote_plus(val)
                            import HTMLParser
                            val=HTMLParser.HTMLParser().unescape(val)
                        try:
                            url = url.replace("$doregex[" + k + "]", val)
                        except: url = url.replace("$doregex[" + k + "]", val.decode("utf-8"))
                        #print 'ur',url
                        #return val
                else:
                    url = url.replace("$doregex[" + k + "]",'')
        if '$epoctime$' in url:
            url=url.replace('$epoctime$',getEpocTime())
        if '$epoctime2$' in url:
            url=url.replace('$epoctime2$',getEpocTime2())

        if '$GUID$' in url:
            import uuid
            url=url.replace('$GUID$',str(uuid.uuid1()).upper())
        if '$get_cookies$' in url:
            url=url.replace('$get_cookies$',getCookiesString(cookieJar))

        if recursiveCall: return url
        #print 'final url',repr(url)
        if url=="":
            return
        else:
            return url,setresolved

def getmd5(t):
    import hashlib
    h=hashlib.md5()
    h.update(t)
    return h.hexdigest()

def decrypt_vaughnlive(encrypted):
    retVal=""
    #print 'enc',encrypted
    #for val in encrypted.split(':'):
    #    retVal+=chr(int(val.replace("0m0","")))
    #return retVal

def playmedia(media_url):
    try:
        listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=media_url )

        if addon.getSetting("use_internal_player") == "true":
            import  CustomPlayer
            player = CustomPlayer.MyXBMCPlayer()
            player.play( media_url,listitem)
            #xbmc.sleep(1000)
            while player.is_active:
                xbmc.sleep(200)
        else:
            xbmc.Player().play(media_url,listitem)
    except:
        traceback.print_exc()
    return ''

def kodiJsonRequest(params):
    data = json.dumps(params)
    request = xbmc.executeJSONRPC(data)

    try:
        response = json.loads(request)
    except UnicodeDecodeError:
        response = json.loads(request.decode('utf-8', 'ignore'))

    try:
        if 'result' in response:
            return response['result']
        return None
    except KeyError:
        logger.warn("[%s] %s" % (params['method'], response['error']['message']))
        return None

def setKodiProxy(proxysettings=None):

    if proxysettings==None:
        #print 'proxy set to nothing'
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.usehttpproxy", "value":false}, "id":1}')
    else:
        
        ps=proxysettings.split(':')
        proxyURL=ps[0]
        proxyPort=ps[1]
        proxyType=ps[2]
        proxyUsername=None
        proxyPassword=None
        
        if len(ps)>3 and '@' in ps[3]: #jairox ###proxysettings
            proxyUsername=ps[3].split('@')[0] #jairox ###ps[3]
            proxyPassword=ps[3].split('@')[1] #jairox ###proxysettings.split('@')[-1]

       #print 'proxy set to', proxyType, proxyURL,proxyPort
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.usehttpproxy", "value":true}, "id":1}')
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.httpproxytype", "value":' + str(proxyType) +'}, "id":1}')
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.httpproxyserver", "value":"' + str(proxyURL) +'"}, "id":1}')
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.httpproxyport", "value":' + str(proxyPort) +'}, "id":1}')
        
        
        if not proxyUsername==None:
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.httpproxyusername", "value":"' + str(proxyUsername) +'"}, "id":1}')
            xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"network.httpproxypassword", "value":"' + str(proxyPassword) +'"}, "id":1}')
       
def getConfiguredProxy():
    proxyActive = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.usehttpproxy"}, 'id': 1})['value']
   #print 'proxyActive',proxyActive
    proxyType = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxytype"}, 'id': 1})['value']

    if proxyActive: # PROXY_HTTP
        proxyURL = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyserver"}, 'id': 1})['value']
        proxyPort = unicode(kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyport"}, 'id': 1})['value'])
        proxyUsername = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxyusername"}, 'id': 1})['value']
        proxyPassword = kodiJsonRequest({'jsonrpc': '2.0', "method":"Settings.GetSettingValue", "params":{"setting":"network.httpproxypassword"}, 'id': 1})['value']

        if proxyUsername and proxyPassword and proxyURL and proxyPort:
            return proxyURL + ':' + str(proxyPort)+':'+str(proxyType) + ':' + proxyUsername + '@' + proxyPassword
        elif proxyURL and proxyPort:
            return proxyURL + ':' + str(proxyPort)+':'+str(proxyType)
    else:
        return None
        
def playmediawithproxy(media_url, name, iconImage,proxyip,port, proxyuser=None, proxypass=None): #jairox

    if media_url==None or media_url=='':
        xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Unable to play empty Url,5000,"+icon+")")
        return
    progress = xbmcgui.DialogProgress()
    progress.create('Progress', 'Playing with custom proxy')
    progress.update( 10, "", "setting proxy..", "" )
    proxyset=False
    existing_proxy=''
    #print 'playmediawithproxy'
    try:
        
        existing_proxy=getConfiguredProxy()
        print 'existing_proxy',existing_proxy
        #read and set here
        #jairox
        if not proxyuser == None:
            setKodiProxy( proxyip + ':' + port + ':0:' + proxyuser + '@' + proxypass)
        else:
            setKodiProxy( proxyip + ':' + port + ':0')

        print 'proxy setting complete playing',media_url
        proxyset=True
        progress.update( 80, "", "setting proxy complete, now playing", "" )
        

        import  CustomPlayer
        player = CustomPlayer.MyXBMCPlayer()
        player.pdialogue==progress
        listitem = xbmcgui.ListItem( label = str(name), iconImage = iconImage, thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=media_url )
        player.play( media_url,listitem)
        xbmc.sleep(1000)
        #while player.is_active:
        #    xbmc.sleep(200)
        import time
        beforestart=time.time()
        try:
            while player.is_active:
                xbmc.sleep(1000)       
                if player.urlplayed==False and time.time()-beforestart>12:
                    print 'failed!!!'
                    xbmc.executebuiltin("XBMC.Notification(LiveStreamsPro,Unable to play check proxy,5000,"+icon+")")
                    break
                #xbmc.sleep(1000)
        except: pass

        progress.close()
        progress=None
    except:
        traceback.print_exc()
    if progress:
        progress.close()
    if proxyset:
        print 'now resetting the proxy back'
        setKodiProxy(existing_proxy)
        print 'reset here'
    return ''

def get_saw_rtmp(page_value, referer=None):
    if referer:
        referer=[('Referer',referer)]
    if page_value.startswith("http"):
        page_url=page_value
        page_value= getUrl(page_value,headers=referer)

    str_pattern="(eval\(function\(p,a,c,k,e,(?:r|d).*)"

    reg_res=re.compile(str_pattern).findall(page_value)
    r=""
    if reg_res and len(reg_res)>0:
        for v in reg_res:
            r1=get_unpacked(v)
            r2=re_me(r1,'\'(.*?)\'')
            if 'unescape' in r1:
                r1=urllib.unquote(r2)
            r+=r1+'\n'

        page_url=re_me(r,'src="(.*?)"')

        page_value= getUrl(page_url,headers=referer)

    #print page_value

    rtmp=re_me(page_value,'streamer\'.*?\'(.*?)\'\)')
    playpath=re_me(page_value,'file\',\s\'(.*?)\'')


    return rtmp+' playpath='+playpath +' pageUrl='+page_url

def get_leton_rtmp(page_value, referer=None):
    if referer:
        referer=[('Referer',referer)]
    if page_value.startswith("http"):
        page_value= getUrl(page_value,headers=referer)
    str_pattern="var a = (.*?);\s*var b = (.*?);\s*var c = (.*?);\s*var d = (.*?);\s*var f = (.*?);\s*var v_part = '(.*?)';"
    reg_res=re.compile(str_pattern).findall(page_value)[0]

    a,b,c,d,f,v=(reg_res)
    f=int(f)
    a=int(a)/f
    b=int(b)/f
    c=int(c)/f
    d=int(d)/f

    ret= 'rtmp://' + str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d) + v
    return ret

def createM3uForDash(url,useragent=None):
    str='#EXTM3U'
    str+='\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=361816'
    str+='\n'+url+'&bytes=0-200000'#+'|User-Agent='+useragent
    source_file = os.path.join(profile, 'testfile.m3u')
    str+='\n'
    SaveToFile(source_file,str)
    #return 'C:/Users/shani/Downloads/test.m3u8'
    return source_file

def SaveToFile(file_name,page_data,append=False):
    if append:
        f = open(file_name, 'a')
        f.write(page_data)
        f.close()
    else:
        f=open(file_name,'wb')
        f.write(page_data)
        f.close()
        return ''

def LoadFile(file_name):
    f=open(file_name,'rb')
    d=f.read()
    f.close()
    return d

def get_packed_iphonetv_url(page_data):
    import re,base64,urllib
    s=page_data
    while 'geh(' in s:
        if s.startswith('lol('): s=s[5:-1]
      #print 's is ',s
        s=re.compile('"(.*?)"').findall(s)[0]
        s=  base64.b64decode(s)
        s=urllib.unquote(s)
    print s
    return s

def get_ferrari_url(page_data):
   #print 'get_dag_url2',page_data
    page_data2=getUrl(page_data)
    patt='(http.*)'
    import uuid
    playback=str(uuid.uuid1()).upper()
    links=re.compile(patt).findall(page_data2)
    headers=[('X-Playback-Session-Id',playback)]
    for l in links:
        try:
                page_datatemp=getUrl(l,headers=headers)

        except: pass

    return page_data+'|&X-Playback-Session-Id='+playback

def get_dag_url(page_data):
   #print 'get_dag_url',page_data
    if page_data.startswith('http://dag.total-stream.net'):
        headers=[('User-Agent','Verismo-BlackUI_(2.4.7.5.8.0.34)')]
        page_data=getUrl(page_data,headers=headers)

    if '127.0.0.1' in page_data:
        return revist_dag(page_data)
    elif re_me(page_data, 'wmsAuthSign%3D([^%&]+)') != '':
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + '?wmsAuthSign=' + re_me(page_data, 'wmsAuthSign%3D([^%&]+)') + '==/mp4:' + re_me(page_data, '\\?y=([^&]+)&')
    else:
        final_url = re_me(page_data, 'href="([^"]+)"[^"]+$')
        if len(final_url)==0:
            final_url=page_data
    final_url = final_url.replace(' ', '%20')
    return final_url

def re_me(data, re_patten):
    match = ''
    m = re.search(re_patten, data)
    if m != None:
        match = m.group(1)
    else:
        match = ''
    return match

def revist_dag(page_data):
    final_url = ''
    if '127.0.0.1' in page_data:
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + ' live=true timeout=15 playpath=' + re_me(page_data, '\\?y=([a-zA-Z0-9-_\\.@]+)')

    if re_me(page_data, 'token=([^&]+)&') != '':
        final_url = final_url + '?token=' + re_me(page_data, 'token=([^&]+)&')
    elif re_me(page_data, 'wmsAuthSign%3D([^%&]+)') != '':
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + '?wmsAuthSign=' + re_me(page_data, 'wmsAuthSign%3D([^%&]+)') + '==/mp4:' + re_me(page_data, '\\?y=([^&]+)&')
    else:
        final_url = re_me(page_data, 'HREF="([^"]+)"')

    if 'dag1.asx' in final_url:
        return get_dag_url(final_url)

    if 'devinlivefs.fplive.net' not in final_url:
        final_url = final_url.replace('devinlive', 'flive')
    if 'permlivefs.fplive.net' not in final_url:
        final_url = final_url.replace('permlive', 'flive')
    return final_url

def get_unwise( str_eval):
    page_value=""
    try:
        ss="w,i,s,e=("+str_eval+')'
        exec (ss)
        page_value=unwise_func(w,i,s,e)
    except: traceback.print_exc(file=sys.stdout)
    #print 'unpacked',page_value
    return page_value

def unwise_func( w, i, s, e):
    lIll = 0
    ll1I = 0
    Il1l = 0
    ll1l = []
    l1lI = []
    while True:
        if (lIll < 5):
            l1lI.append(w[lIll])
        elif (lIll < len(w)):
            ll1l.append(w[lIll])
        lIll+=1
        if (ll1I < 5):
            l1lI.append(i[ll1I])
        elif (ll1I < len(i)):
            ll1l.append(i[ll1I])
        ll1I+=1
        if (Il1l < 5):
            l1lI.append(s[Il1l])
        elif (Il1l < len(s)):
            ll1l.append(s[Il1l])
        Il1l+=1
        if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
            break

    lI1l = ''.join(ll1l)#.join('');
    I1lI = ''.join(l1lI)#.join('');
    ll1I = 0
    l1ll = []
    for lIll in range(0,len(ll1l),2):
        #print 'array i',lIll,len(ll1l)
        ll11 = -1
        if ( ord(I1lI[ll1I]) % 2):
            ll11 = 1
        #print 'val is ', lI1l[lIll: lIll+2]
        l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11))
        ll1I+=1
        if (ll1I >= len(l1lI)):
            ll1I = 0
    ret=''.join(l1ll)
    if 'eval(function(w,i,s,e)' in ret:
        ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0]
        return get_unwise(ret)
    else:
        return ret

def get_unpacked( page_value, regex_for_text='', iterations=1, total_iteration=1):
    try:
        reg_data=None
        if page_value.startswith("http"):
            page_value= getUrl(page_value)
        if regex_for_text and len(regex_for_text)>0:
            try:
                page_value=re.compile(regex_for_text).findall(page_value)[0] #get the js variable
            except: return 'NOTPACKED'

        page_value=unpack(page_value,iterations,total_iteration)
    except:
        page_value='UNPACKEDFAILED'
        traceback.print_exc(file=sys.stdout)
    if 'sav1live.tv' in page_value:
        page_value=page_value.replace('sav1live.tv','sawlive.tv') #quick fix some bug somewhere
    return page_value

def unpack(sJavascript,iteration=1, totaliterations=2  ):
    if sJavascript.startswith('var _0xcb8a='):
        aSplit=sJavascript.split('var _0xcb8a=')
        ss="myarray="+aSplit[1].split("eval(")[0]
        exec(ss)
        a1=62
        c1=int(aSplit[1].split(",62,")[1].split(',')[0])
        p1=myarray[0]
        k1=myarray[3]
        with open('temp file'+str(iteration)+'.js', "wb") as filewriter:
            filewriter.write(str(k1))
        #aa=1/0
    else:

        if "rn p}('" in sJavascript:
            aSplit = sJavascript.split("rn p}('")
        else:
            aSplit = sJavascript.split("rn A}('")

        p1,a1,c1,k1=('','0','0','')

        ss="p1,a1,c1,k1=('"+aSplit[1].split(".spli")[0]+')'
        exec(ss)
    k1=k1.split('|')
    aSplit = aSplit[1].split("))'")


    #p=str(aSplit[0]+'))')#.replace("\\","")#.replace('\\\\','\\')

    #print aSplit[1]
    #aSplit = aSplit[1].split(",")
    #print aSplit[0]
    #a = int(aSplit[1])
    #c = int(aSplit[2])
    #k = aSplit[3].split(".")[0].replace("'", '').split('|')
    #a=int(a)
    #c=int(c)

    #p=p.replace('\\', '')


    #print a,a1
    #print c,a1

    e = ''
    d = ''#32823

    #sUnpacked = str(__unpack(p, a, c, k, e, d))
    sUnpacked1 = str(__unpack(p1, a1, c1, k1, e, d,iteration))

    #print sUnpacked[:200]+'....'+sUnpacked[-100:], len(sUnpacked)

    #exec('sUnpacked1="'+sUnpacked1+'"')
    if iteration>=totaliterations:
        return sUnpacked1#.replace('\\\\', '\\')
    else:
        return unpack(sUnpacked1,iteration+1)#.replace('\\', ''),iteration)#.replace('\\', '');#unpack(sUnpacked.replace('\\', ''))

def __unpack(p, a, c, k, e, d, iteration,v=1):

    #with open('before file'+str(iteration)+'.js', "wb") as filewriter:
    while (c >= 1):
        c = c -1
        if (k[c]):
            aa=str(__itoaNew(c, a))
            if v==1:
                p=re.sub('\\b' + aa +'\\b', k[c], p)# THIS IS Bloody slow!
            else:
                p=findAndReplaceWord(p,aa,k[c])

            #p=findAndReplaceWord(p,aa,k[c])


    #with open('after file'+str(iteration)+'.js', "wb") as filewriter:
    return p

#function equalavent to re.sub('\\b' + aa +'\\b', k[c], p)
def findAndReplaceWord(source_str, word_to_find,replace_with):
    splits=None
    splits=source_str.split(word_to_find)
    if len(splits)>1:
        new_string=[]
        current_index=0
        for current_split in splits:
            #print 'here',i
            new_string.append(current_split)
            val=word_to_find#by default assume it was wrong to split

            #if its first one and item is blank then check next item is valid or not
            if current_index==len(splits)-1:
                val='' # last one nothing to append normally
            else:
                if len(current_split)==0: #if blank check next one with current split value
                    if ( len(splits[current_index+1])==0 and word_to_find[0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') or (len(splits[current_index+1])>0  and splits[current_index+1][0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_'):# first just just check next
                        val=replace_with
                #not blank, then check current endvalue and next first value
                else:
                    if (splits[current_index][-1].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') and (( len(splits[current_index+1])==0 and word_to_find[0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') or (len(splits[current_index+1])>0  and splits[current_index+1][0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_')):# first just just check next
                        val=replace_with

            new_string.append(val)
            current_index+=1
        #aaaa=1/0
        source_str=''.join(new_string)
    return source_str

def __itoa(num, radix):
    result = ""
    if num==0: return '0'
    while num > 0:
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
        num /= radix
    return result

def __itoaNew(cc, a):
    aa="" if cc < a else __itoaNew(int(cc / a),a)
    cc = (cc % a)
    bb=chr(cc + 29) if cc> 35 else str(__itoa(cc,36))
    return aa+bb

def getCookiesString(cookieJar):
    try:
        cookieString=""
        for index, cookie in enumerate(cookieJar):
            cookieString+=cookie.name + "=" + cookie.value +";"
    except: pass
    #print 'cookieString',cookieString
    return cookieString

def saveCookieJar(cookieJar,COOKIEFILE):
    try:
        complete_path=os.path.join(profile,COOKIEFILE)
        cookieJar.save(complete_path,ignore_discard=True)
    except: pass

def getCookieJar(COOKIEFILE):

    cookieJar=None
    if COOKIEFILE:
        try:
            complete_path=os.path.join(profile,COOKIEFILE)
            cookieJar = cookielib.LWPCookieJar()
            cookieJar.load(complete_path,ignore_discard=True)
        except:
            cookieJar=None

    if not cookieJar:
        cookieJar = cookielib.LWPCookieJar()

    return cookieJar

def doEval(fun_call,page_data,Cookie_Jar,m):
    ret_val=''
    #print fun_call
    if functions_dir not in sys.path:
        sys.path.append(functions_dir)

    try:
        py_file='import '+fun_call.split('.')[0]
        exec( py_file)

    except:
        print 'doEval: error in import'
    exec ('ret_val='+fun_call)
    try:
        return str(ret_val)
    except: return ret_val

def doEvalFunction(fun_call,page_data,Cookie_Jar,m):
    try:
        global gLSProDynamicCodeNumber
        gLSProDynamicCodeNumber=gLSProDynamicCodeNumber+1
        ret_val=''
        print 'doooodoo'
        if functions_dir not in sys.path:
            sys.path.append(functions_dir)

        filename='LSProdynamicCode%s.py'%str(gLSProDynamicCodeNumber)
        filenamewithpath=os.path.join(functions_dir,filename)
        f=open(filenamewithpath,"wb")
        f.write("# -*- coding: utf-8 -*-\n")
        f.write(fun_call.encode("utf-8"))
        f.close()
        print 'before do'
        LSProdynamicCode = import_by_string(filename.split('.')[0],filenamewithpath)
        print 'after'
         
        ret_val=LSProdynamicCode.GetLSProData(page_data,Cookie_Jar,m)
        try:
            return str(ret_val)
        except: return ret_val
    except: traceback.print_exc()
    return ""

def import_by_string(full_name,filenamewithpath):
    try:
        
        import importlib
        return importlib.import_module(full_name, package=None)
    except:
        import imp
        return imp.load_source(full_name,filenamewithpath)

def getGoogleRecaptchaResponse(captchakey, cj,type=1): #1 for get, 2 for post, 3 for rawpost
    recapChallenge=""
    solution=""
    captcha=False
    captcha_reload_response_chall=None
    solution=None
    if len(captchakey)>0: #new shiny captcha!
        captcha_url=captchakey
        if not captcha_url.startswith('http'):
            captcha_url='http://www.google.com/recaptcha/api/challenge?k='+captcha_url+'&ajax=1'
        captcha=True

        cap_chall_reg='challenge.*?\'(.*?)\''
        cap_image_reg='\'(.*?)\''
        captcha_script=getUrl(captcha_url,cookieJar=cj)
        recapChallenge=re.findall(cap_chall_reg, captcha_script)[0]
        captcha_reload='http://www.google.com/recaptcha/api/reload?c='
        captcha_k=captcha_url.split('k=')[1]
        captcha_reload+=recapChallenge+'&k='+captcha_k+'&reason=i&type=image&lang=en'
        captcha_reload_js=getUrl(captcha_reload,cookieJar=cj)
        captcha_reload_response_chall=re.findall(cap_image_reg, captcha_reload_js)[0]
        captcha_image_url='http://www.google.com/recaptcha/api/image?c='+captcha_reload_response_chall
        if not captcha_image_url.startswith("http"):
            captcha_image_url='http://www.google.com/recaptcha/api/'+captcha_image_url
        import random
        n=random.randrange(100,1000,5)
        local_captcha = os.path.join(profile,str(n) +"captcha.img" )
        localFile = open(local_captcha, "wb")
        localFile.write(getUrl(captcha_image_url,cookieJar=cj))
        localFile.close()
        solver = InputWindow(captcha=local_captcha)
        solution = solver.get()
        os.remove(local_captcha)

    if captcha_reload_response_chall:
        if type==1:
            return 'recaptcha_challenge_field='+urllib.quote_plus(captcha_reload_response_chall)+'&recaptcha_response_field='+urllib.quote_plus(solution)
        elif type==2:
            return 'recaptcha_challenge_field:'+captcha_reload_response_chall+',recaptcha_response_field:'+solution
        else:
            return 'recaptcha_challenge_field='+urllib.quote_plus(captcha_reload_response_chall)+'&recaptcha_response_field='+urllib.quote_plus(solution)
    else:
        return ''

def getUrl(url, cookieJar=None,post=None, timeout=20, headers=None, noredir=False):


    cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)

    if noredir:
        opener = urllib2.build_opener(NoRedirection,cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    else:
        opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    #opener = urllib2.install_opener(opener)
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    if headers:
        for h,hv in headers:
            req.add_header(h,hv)

    response = opener.open(req,post,timeout=timeout)
    link=response.read()
    response.close()
    return link

def get_decode(str,reg=None):
    if reg:
        str=re.findall(reg, str)[0]
    s1 = urllib.unquote(str[0: len(str)-1])
    t = ''
    for i in range( len(s1)):
        t += chr(ord(s1[i]) - s1[len(s1)-1])
    t=urllib.unquote(t)
    return t

def javascriptUnEscape(str):
    js=re.findall('unescape\(\'(.*?)\'',str)
    if (not js==None) and len(js)>0:
        for j in js:
            #print urllib.unquote(j)
            str=str.replace(j ,urllib.unquote(j))
    return str

def askCaptcha(m,html_page, cookieJar):
    global iid
    iid+=1
    expre= m['expres']
    page_url = m['page']
    captcha_regex=re.compile('\$LiveStreamCaptcha\[([^\]]*)\]').findall(expre)[0]

    captcha_url=re.compile(captcha_regex).findall(html_page)[0]
    if not captcha_url.startswith("http"):
        page_='http://'+"".join(page_url.split('/')[2:3])
        if captcha_url.startswith("/"):
            captcha_url=page_+captcha_url
        else:
            captcha_url=page_+'/'+captcha_url

    local_captcha = os.path.join(profile, str(iid)+"captcha.jpg" )
    localFile = open(local_captcha, "wb")
    req = urllib2.Request(captcha_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
    if 'referer' in m:
        req.add_header('Referer', m['referer'])
    if 'agent' in m:
        req.add_header('User-agent', m['agent'])
    if 'setcookie' in m:
        req.add_header('Cookie', m['setcookie'])

    #cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    #opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    #opener = urllib2.install_opener(opener)
    urllib2.urlopen(req)
    response = urllib2.urlopen(req)

    localFile.write(response.read())
    response.close()
    localFile.close()
    solver = InputWindow(captcha=local_captcha)
    solution = solver.get()
    return solution

def askCaptchaNew(imageregex,html_page,cookieJar,m):
    global iid
    iid+=1


    if not imageregex=='':
        if html_page.startswith("http"):
            page_=getUrl(html_page,cookieJar=cookieJar)
        else:
            page_=html_page
        captcha_url=re.compile(imageregex).findall(html_page)[0]
    else:
        captcha_url=html_page
        if 'oneplay.tv/embed' in html_page:
            import oneplay
            page_=getUrl(html_page,cookieJar=cookieJar)
            captcha_url=oneplay.getCaptchaUrl(page_)

    local_captcha = os.path.join(profile, str(iid)+"captcha.jpg" )
    localFile = open(local_captcha, "wb")
    req = urllib2.Request(captcha_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
    if 'referer' in m:
        req.add_header('Referer', m['referer'])
    if 'agent' in m:
        req.add_header('User-agent', m['agent'])
    if 'accept' in m:
        req.add_header('Accept', m['accept'])
    if 'setcookie' in m:
        req.add_header('Cookie', m['setcookie'])

    #cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    #opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
    #opener = urllib2.install_opener(opener)
    #urllib2.urlopen(req)
    response = urllib2.urlopen(req)

    localFile.write(response.read())
    response.close()
    localFile.close()
    solver = InputWindow(captcha=local_captcha)
    solution = solver.get()
    return solution

def TakeInput(name, headname):
    kb = xbmc.Keyboard('default', 'heading', True)
    kb.setDefault(name)
    kb.setHeading(headname)
    kb.setHiddenInput(False)
    return kb.getText()


def getEpocTime():
    import time
    return str(int(time.time()*1000))

def getEpocTime2():
    import time
    return str(int(time.time()))

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

def tryplay(url,listitem,pdialogue=None):    

    if url.lower().startswith('plugin') and 'youtube' not in  url.lower():
        print 'playing via runplugin'
        xbmc.executebuiltin('XBMC.RunPlugin('+url+')') 
        for i in range(8):
            xbmc.sleep(500) ##sleep for 10 seconds, half each time
            try:
                #print 'condi'
                if xbmc.getCondVisibility("Player.HasMedia") and xbmc.Player().isPlaying():
                    return True
            except: pass
        print 'returning now'
        return False
    if addon.getSetting("use_internal_player") == "true":
        import  CustomPlayer,time
        player = CustomPlayer.MyXBMCPlayer()
        player.pdialogue=pdialogue
        #xbmc.Player().play( liveLink,listitem)
        print 'going to play'
        force_reload = addon.getSetting("force_reload")
        start_time_play=time.time()
        player.play( url, listitem)
        xbmc.sleep(1000)
    else:
        xbmc.Player().play(url, listitem)
    return true
    ''' old code
    try:
        while player.is_active:
            xbmc.sleep(400)
           
            if player.urlplayed:
                print 'yes played'
                return True
            if time.time()-beforestart>4: return False
            #xbmc.sleep(1000)
    except: pass
    print 'not played',url
    return False
    '''

def play_playlist(name, mu_playlist,queueVideo=None):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #print 'mu_playlist',mu_playlist
        if '$$LSPlayOnlyOne$$' in mu_playlist[0]:
            mu_playlist[0]=mu_playlist[0].replace('$$LSPlayOnlyOne$$','')
            import urlparse
            names = []
            iloop=0
            progress = xbmcgui.DialogProgress()
            progress.create('Progress', 'Trying Multiple Links')
            for i in mu_playlist:
                

                if '$$lsname=' in i:
                    d_name=i.split('$$lsname=')[1].split('&regexs')[0]
                    names.append(d_name)                                       
                    mu_playlist[iloop]=i.split('$$lsname=')[0]+('&regexs'+i.split('&regexs')[1] if '&regexs' in i else '')                    
                else:
                    d_name=urlparse.urlparse(i).netloc
                    if d_name == '':
                        names.append(name)
                    else:
                        names.append(d_name)
                index=iloop
                iloop+=1
                
                playname=names[index]
                if progress.iscanceled(): return 
                progress.update( iloop/len(mu_playlist)*100,"", "Link#%d"%(iloop),playname  )
                print 'auto playnamexx',playname
                if "&mode=19" in mu_playlist[index]:
                        #playsetresolved (urlsolver(mu_playlist[index].replace('&mode=19','')),name,iconimage,True)
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    urltoplay=urlsolver(mu_playlist[index].replace('&mode=19','').replace(';',''))
                    liz.setPath(urltoplay)
                    #xbmc.Player().play(urltoplay,liz)
                    played=tryplay(urltoplay,liz)
                elif "$doregex" in mu_playlist[index] :
                    sepate = mu_playlist[index].split('&regexs=')
                    url,setresolved = getRegexParsed(sepate[1], sepate[0])
                    url2 = url.replace(';','')
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    liz.setPath(url2)
                    #xbmc.Player().play(url2,liz)
                    played=tryplay(url2,liz)

                else:
                    url = mu_playlist[index]
                    url=url.split('&regexs=')[0]
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    liz.setPath(url)
                    #xbmc.Player().play(url,liz)
                    played=tryplay(url,liz)
                    print 'played',played
                print 'played',played
                if played: return
            return     
        if addon.getSetting('ask_playlist_items') == 'true' and not queueVideo :
            import urlparse
            names = []
            iloop=0
            for i in mu_playlist:
                if '$$lsname=' in i:
                    d_name=i.split('$$lsname=')[1].split('&regexs')[0]
                    names.append(d_name)                                       
                    mu_playlist[iloop]=i.split('$$lsname=')[0]+('&regexs'+i.split('&regexs')[1] if '&regexs' in i else '')                    
                else:
                    d_name=urlparse.urlparse(i).netloc
                    if d_name == '':
                        names.append(name)
                    else:
                        names.append(d_name)
                    
                iloop+=1
            dialog = xbmcgui.Dialog()
            index = dialog.select('Choose a video source', names)
            if index >= 0:
                playname=names[index]
                print 'playnamexx',playname
                if "&mode=19" in mu_playlist[index]:
                        #playsetresolved (urlsolver(mu_playlist[index].replace('&mode=19','')),name,iconimage,True)
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    urltoplay=urlsolver(mu_playlist[index].replace('&mode=19','').replace(';',''))
                    liz.setPath(urltoplay)
                    xbmc.Player().play(urltoplay,liz)
                elif "$doregex" in mu_playlist[index] :
                    sepate = mu_playlist[index].split('&regexs=')
                    url,setresolved = getRegexParsed(sepate[1], sepate[0])
                    url2 = url.replace(';','')
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    liz.setPath(url2)
                    xbmc.Player().play(url2,liz)

                else:
                    url = mu_playlist[index]
                    url=url.split('&regexs=')[0]
                    liz = xbmcgui.ListItem(playname, iconImage=iconimage, thumbnailImage=iconimage)
                    liz.setInfo(type='Video', infoLabels={'Title':playname})
                    liz.setProperty("IsPlayable","true")
                    liz.setPath(url)
                    xbmc.Player().play(url,liz)
        elif not queueVideo:
            #playlist = xbmc.PlayList(1) # 1 means video
            playlist.clear()
            item = 0
            for i in mu_playlist:
                item += 1
                info = xbmcgui.ListItem('%s) %s' %(str(item),name))
                # Don't do this as regex parsed might take longer
                try:
                    if "$doregex" in i:
                        sepate = i.split('&regexs=')
                        url,setresolved = getRegexParsed(sepate[1], sepate[0])
                    elif "&mode=19" in i:
                        url = urlsolver(i.replace('&mode=19','').replace(';',''))                        
                    if url:
                        playlist.add(url, info)
                    else:
                        raise
                except Exception:
                    playlist.add(i, info)
                    pass #xbmc.Player().play(url)

            xbmc.executebuiltin('playlist.playoffset(video,0)')
        else:

                listitem = xbmcgui.ListItem(name)
                playlist.add(mu_playlist, listitem)

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
                    
            if name in str(SOURCES):
                    contextMenu.append(('Remove from Sources','XBMC.RunPlugin(%s?mode=8&name=%s)' %(sys.argv[0], urllib.quote_plus(name))))

            if addon.getSetting("enable_download") == "true":
                contextMenu.append(('Download','XBMC.RunPlugin(%s?url=%s&mode=9&name=%s)' %(sys.argv[0], urllib.quote_plus(url), urllib.quote_plus(name))))
            
            if showcontext == 'fav':
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
                    play_playlist(name,url,queueVideo='1')
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
            addon_log('NOT setting isplayable'+url)
        
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

def playsetresolved(url,name,iconimage,setresolved=True,reg=None):
    #print 'playsetresolved',url,name,setresolved
    print 'playsetresolved'
    if url==None: 
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return

    if '&mode=22' in url:
        setresolved=False
        url=url.replace('&mode=22','')
        u=sys.argv[0]+"?"
        u += "url="+urllib.quote_plus(url)+"&name="+urllib.quote(name)+"&mode=22"
        url = u

    if setresolved:
        setres=True
        if '$$LSDirect$$' in url:
            url=url.replace('$$LSDirect$$','')
            setres=False
        if reg and 'notplayable' in reg:
            setres=False

        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo(type='Video', infoLabels={'Title':name})
        liz.setProperty("IsPlayable","true")
        if '&mode=19' in url:
            url=urlsolver(url.replace('&mode=19','').replace(';',''))
        elif '&mode=20' in url:
            url=url.replace('&mode=20','')
            if '|' in url:
                url,strhdr = url.split('|')
                liz.setProperty('inputstream.adaptive.stream_headers', strhdr)
				
            if '.m3u8' in url:
                liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
                liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
                liz.setMimeType('application/vnd.apple.mpegstream_url')
                liz.setContentLookup(False)

            
            elif '.mpd' in url:
                liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
                liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                liz.setMimeType('application/dash+xml')
                liz.setContentLookup(False)
            
            elif '.ism' in url:
                liz.setProperty('inputstreamaddon', 'inputstream.adaptive')
                liz.setProperty('inputstream.adaptive.manifest_type', 'ism')
                liz.setMimeType('application/vnd.ms-sstr+xml')
                liz.setContentLookup(False)
        
        # elif '&mode=22' in url:
        #     print "slproxy"
        #     url=url.replace('&mode=22','')
        #     try:
        #         from dsp import streamlink_proxy
        #         slProxy = streamlink_proxy.SLProxy_Helper()
        #         try:
        #             q =  re.findall(r'\$\$QUALITY=([^\$\$]+)\$\$', url)[0]
        #         except:
        #             q = 'best'
        #         url = re.sub(r'\$\$QUALITY=.*?\$\$', '', url)
        #         url = urllib.quote(url)+'&amp;q=%s'%q
        #         liz.setPath(url)
        #         liz.setProperty("IsPlayable","false")
        #         slProxy.playSLink(url, liz)
        #         return
        #    except:
        #        pass

        liz.setPath(url)
        if not setres:
            xbmc.Player().play(url)
        else:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
           
    else:
        xbmc.executebuiltin('XBMC.RunPlugin('+url+')')

def getepg(link):
    ## Thanks to daschacka, an epg scraper for http://i.teleboy.ch/programm/station_select.php
    ##  http://forum.xbmc.org/post.php?p=936228&postcount=1076
    url=urllib.urlopen(link)
    source=url.read()
    url.close()
    source2 = source.split("Jetzt")
    source3 = source2[1].split('programm/detail.php?const_id=')
    sourceuhrzeit = source3[1].split('<br /><a href="/')
    nowtime = sourceuhrzeit[0][40:len(sourceuhrzeit[0])]
    sourcetitle = source3[2].split("</a></p></div>")
    nowtitle = sourcetitle[0][17:len(sourcetitle[0])]
    nowtitle = nowtitle.encode('utf-8')
    return "  - "+nowtitle+" - "+nowtime

def get_epg(url, regex):
        data = makeRequest(url)
        try:
            item = re.findall(regex, data)[0]
            return item
        except:
            addon_log('regex failed')
            addon_log(regex)
            return
