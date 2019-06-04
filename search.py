# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, xbmcgui, sys, os, re, urllib, urllib2
addon = xbmcaddon.Addon('plugin.video.livestreamspro')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
source_file = os.path.join(profile, 'source_file')
try:
    import json
except:
    import simplejson as json
    
if addon.getSetting('tsdownloader') == 'true':
    tsdownloader = True
if addon.getSetting('hlsretry') == 'true' :
    hlsretry = True


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

def search(name, content):
    result = os.path.join(profile, "search_result.xml")
    result_file = open(result, "w")

    links = []
    if os.path.exists(source_file)==True:
        sources = json.loads(open(source_file,"r").read())

    if content != "all":
        filter_list = True
    else:
        filter_list = False

    for source in sources:
        if "http" in source['url']:
            item = {}
            item["url"] = source['url']
            if source["title"]:
                item["title"] = source['title']
            print "##### FILTER LIST IS #####" + str(filter_list)
            if filter_list is True:
                if content == source['media_type']:
                    links.append(item)
            else:
                links.append(item)

    dp = xbmcgui.DialogProgress()
    current_element = 0
    total_elements = len(links)
    dp.create("Live Streams Pro","Searcning in: ", "Total: " + str(current_element)+"/"+str(total_elements) )

    for link in links:
        try:
            current_element = int(current_element) + 1
            percent = min((int(current_element)*100)/int(total_elements), 100)
            dp.update(percent, "Searching in: " + link["title"], "Total: " + str(current_element)+"/"+str(total_elements) )
            if dp.iscanceled():
                return True
            source_url_name = link["title"]
            content = makeRequest(link["url"])
            if "EXTM3U" in content or "EXTINF" in content:
                items = re.compile('#EXTINF:.+?\,(.+?)\n(.+?)\n', re.MULTILINE | re.DOTALL).findall(content)
                print items
                for item in items:
                    try: title = list(item)[0].replace("\n", "").replace("\r", "").replace("\t", "")
                    except: title = None
                    try: link = list(item)[1].replace("\n", "").replace("\r", "").replace(" ", "").replace("\t", "")
                    except: link = None
                    
                    if addon.getSetting("logo_epg_enable") == "true" and addon.getSetting('logo-folderPath') != "":
                        logo_url = addon.getSetting('logo-folderPath')
                        thumbnail = logo_url + title + ".png"
                    else:
                        thumbnail = ''
                    
                    if 1:
                        if name.lower() in title.lower():
                            if '.ts' in link:
                                link = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(link)+'&amp;streamtype=TSDOWNLOADER&name='+urllib.quote(title)
                            elif '.m3u8' in link:
                                link = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(link)+'&amp;streamtype=HLSRETRY&name='+urllib.quote(title)
                            elif addon.getSetting("force_proxy") == "true":
                                link = 'plugin://plugin.video.f4mTester/?url='+urllib.quote_plus(link)+'&amp;streamtype=SIMPLE&name='+urllib.quote(title)
                            else:
                                link = link               
           
                            result_file.write("<item>\n" + "<title>" + title + " - " + source_url_name + "</title>\n<link>" + link + "</link>\n<thumbnail>" + thumbnail + "</thumbnail>\n</item>")
            else:
                items = re.findall('<item>(.*?)</item>', content, re.DOTALL)
                for item in items:
                    try: title = re.findall('<title>(.*?)</title>', item)[0]
                    except: title = ""
                    try: urlsolve = re.findall('<urlsolve>(.*?)</urlsolve>', item)[0]
                    except: urlsolve = ""
                    try: info = re.findall('<info>(.*?)</info>', item)[0]
                    except: info = ""
                    try: thumbnail = re.findall('<thumbnail>(.*?)</thumbnail>', item)[0]
                    except: thumbnail = ""
                    try: externallink = re.findall('<externallink>(.*?)</externallink>', item)[0]
                    except: externallink = ""
                    try: link = re.findall('<link>(.*?)</link>', item)[0]
                    except: link = None
                    try: regex = re.findall('<regex>(.*?)</regex>', item, re.DOTALL)[0]
                    except: regex = None
                    #try: jsonrpc = re.findall('<jsonrpc>(.*?)</jsonrpc>', item)
                    #except: pass
                    if 1:
                        if name.lower() in title.lower():
                            result_file.write("<item>\n")
                            result_file.write("<title>" + title + " - " + source_url_name + "</title>\n") 
                            if urlsolve != "":    
                                result_file.write("<urlsolve>" + urlsolve + "</urlsolve>\n")
                            result_file.write("<info>" + info + "</info>\n" + "<thumbnail>" + thumbnail + "</thumbnail>\n")
                            if link is None and urlsolve == "":
                                result_file.write("<link>ignore</link>")
                            if link is not None:
                                result_file.write("<link>"+link+"</link>")
                            if regex is not None:
                                result_file.write("<regex>"+regex+"</regex>")
                            if externallink != "":
                                result_file.write("<externallink>" + externallink + "</externallink>\n")
                            result_file.write("</item>")
                            #if link is not None:
                            #    result_file.write("<link>" + link + "</link>\n")
                    else:
                        pass
        except:
            pass
    result_file.close()
    return True
