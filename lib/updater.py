# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# pelisalacarta 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# --------------------------------------------------------------------------------
# Updater process
# --------------------------------------------------------------------------------

import os
import re
import time
import urllib
import urllib2
import xbmc
import xbmcgui
import xbmcaddon

addon = xbmcaddon.Addon('plugin.video.live.streamspro')
ROOT_DIR = xbmc.translatePath(addon.getAddonInfo('Path'))

REMOTE_VERSION_FILE = "https://raw.githubusercontent.com/cttynul/xbmcttynul/master//addons/versionlsp.xml"
REMOTE_FILE = "https://raw.githubusercontent.com/cttynul/xbmcttynul/master//addons/plugin.video.live.streamspro.zip"
LOCAL_VERSION_FILE = addon.getAddonInfo('version')

LOCAL_FILE = os.path.join(ROOT_DIR, "plugin.video.live.streamspro" + ".zip")

# DESTINATION_FOLDER sera siempre el lugar donde este la carpeta del plugin,
# No hace falta "xbmc.translatePath", get_runtime_path() ya tiene que devolver la ruta correcta
DESTINATION_FOLDER = os.path.join(ROOT_DIR, "..")

def check_for_updates():
    req = urllib2.Request(REMOTE_VERSION_FILE)
    response = urllib2.urlopen(req)
    remote_version = response.read()
    #remote_version_temp = response.read().replace(".", ";")
    response.close()

    #remote_version = re.compile('<addon id.+?version="([0-9;]*)', re.MULTILINE | re.DOTALL).findall(remote_version_temp)[0]

    LOCAL_VERSION = int(str(LOCAL_VERSION_FILE.replace(".", "")))
    REMOTE_VERSION = int(str(remote_version.replace(".", "")))

    print "####### LOCAL " + str(LOCAL_VERSION)
    print "####### REMOTE " + str(remote_version)

    if int(REMOTE_VERSION) > int(LOCAL_VERSION):
        xbmcgui.Dialog().ok(str(addon.getAddonInfo('name')), "A new version (" + str(REMOTE_VERSION) + ") of " + str(addon.getAddonInfo('name')) +" is available, update will be installed automagically!")
        try:
            update()
        except:
            xbmcgui.Dialog().ok(str(addon.getAddonInfo('name')), "Ops! Something happened during download and installing of update, version " + str(REMOTE_VERSION))
        xbmcgui.Dialog().ok(str(addon.getAddonInfo('name')), "" + str(addon.getAddonInfo('name')) +" has been updated to " + str(REMOTE_VERSION) + " correctly and automagically.")

def update():
    #xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    remotefilename = REMOTE_FILE
    localfilename = LOCAL_FILE
    download_and_install(remotefilename, localfilename)
    #xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

def download_and_install(remote_file_name, local_file_name):
    if os.path.exists(local_file_name):
        os.remove(local_file_name)

    #downloadfile(remote_file_name, local_file_name, continuar=False)
    #urllib.urlretrieve(remote_file_name,local_file_name)
    url = remote_file_name
    dp = xbmcgui.DialogProgress()
    dp.create("Live Streams Pro","Downloading update")
    urllib.urlretrieve(url, local_file_name, lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))

    from lib import ziptools
    unzipper = ziptools.ziptools()

    installation_target = os.path.join(xbmc.translatePath(addon.getAddonInfo('Path')), "..")
    unzipper.extract(local_file_name, installation_target)
    os.remove(local_file_name)

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

def downloadfile(url, nombrefichero, headers=None, silent=False, continuar=False, resumir=True):

    if headers is None:
        headers = []

    progreso = None

    if nombrefichero.startswith("special://"):
        import xbmc
        nombrefichero = xbmc.translatePath(nombrefichero)

    try:
        # Si no es XBMC, siempre a "Silent"

        # antes
        # f=open(nombrefichero,"wb")
        try:
            import xbmc
            nombrefichero = xbmc.makeLegalFilename(nombrefichero)
        except:
            pass

        # El fichero existe y se quiere continuar
        if os.path.exists(nombrefichero) and continuar:
            f = open(nombrefichero, 'r+b')
            if resumir:
                exist_size = os.path.getsize(nombrefichero)
                grabado = exist_size
                f.seek(exist_size)
            else:
                exist_size = 0
                grabado = 0

        elif os.path.exists(nombrefichero) and not continuar:
            return -3

        # el fichero no existe
        else:
            exist_size = 0
            f = open(nombrefichero, 'wb')
            grabado = 0

        # Crea el diálogo de progreso
        if not silent:
            progreso = dialog_progress("Download", "Downloading...", url, nombrefichero)

        # Si la plataforma no devuelve un cuadro de diálogo válido, asume modo silencio
        if progreso is None:
            silent = True

        if "|" in url:
            additional_headers = url.split("|")[1]
            if "&" in additional_headers:
                additional_headers = additional_headers.split("&")
            else:
                additional_headers = [additional_headers]

            for additional_header in additional_headers:
                name = re.findall("(.*?)=.*?", additional_header)[0]
                value = urllib.unquote_plus(re.findall(".*?=(.*?)$", additional_header)[0])
                headers.append([name, value])

            url = url.split("|")[0]

        # Timeout del socket a 60 segundos
        socket.setdefaulttimeout(60)

        h = urllib2.HTTPHandler(debuglevel=0)
        request = urllib2.Request(url)
        for header in headers:
            request.add_header(header[0], header[1])

        if exist_size > 0:
            request.add_header('Range', 'bytes=%d-' % (exist_size,))

        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)
        try:
            connexion = opener.open(request)
        except urllib2.HTTPError, e:
            # print e.code
            # print e.msg
            # print e.hdrs
            # print e.fp
            f.close()
            if not silent:
                progreso.close()
            # El error 416 es que el rango pedido es mayor que el fichero => es que ya está completo
            if e.code == 416:
                return 0
            else:
                return -2

        try:
            totalfichero = int(connexion.headers["Content-Length"])
        except ValueError:
            totalfichero = 1

        if exist_size > 0:
            totalfichero = totalfichero + exist_size

        blocksize = 100 * 1024
        bloqueleido = connexion.read(blocksize)

        maxreintentos = 10

        while len(bloqueleido) > 0:
            try:
                # Escribe el bloque leido
                f.write(bloqueleido)
                grabado += len(bloqueleido)
                percent = int(float(grabado) * 100 / float(totalfichero))
                totalmb = float(float(totalfichero) / (1024 * 1024))
                descargadosmb = float(float(grabado) / (1024 * 1024))

                # Lee el siguiente bloque, reintentando para no parar todo al primer timeout
                reintentos = 0
                while reintentos <= maxreintentos:
                    try:
                        before = time.time()
                        bloqueleido = connexion.read(blocksize)
                        after = time.time()
                        if (after - before) > 0:
                            velocidad = len(bloqueleido) / (after - before)
                            falta = totalfichero - grabado
                            if velocidad > 0:
                                tiempofalta = falta / velocidad
                            else:
                                tiempofalta = 0
                            if not silent:
                                #progreso.update( percent , "Descargando %.2fMB de %.2fMB (%d%%)" % ( descargadosmb , totalmb , percent),"Falta %s - Velocidad %.2f Kb/s" % ( sec_to_hms(tiempofalta) , velocidad/1024 ), os.path.basename(nombrefichero) )
                                progreso.update( percent , "%.2fMB/%.2fMB (%d%%) %.2f Kb/s manca %s " % ( descargadosmb , totalmb , percent , velocidad/1024 , sec_to_hms(tiempofalta)))
                        break
                    except:
                        reintentos += 1
                        import traceback

                # El usuario cancelo la descarga
                try:
                    if progreso.iscanceled():
                        f.close()
                        progreso.close()
                        return -1
                except:
                    pass

                # Ha habido un error en la descarga
                if reintentos > maxreintentos:
                    f.close()
                    if not silent:
                        progreso.close()

                    return -2

            except:
                import traceback

                f.close()
                if not silent:
                    progreso.close()

                # platformtools.dialog_ok('Error al descargar' , 'Se ha producido un error' , 'al descargar el archivo')

                return -2

    except:
        pass
    try:
        f.close()
    except:
        pass

    if not silent:
        try:
            progreso.close()
        except:
            pass

def dialog_progress(heading, line1, line2=" ", line3=" "):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog