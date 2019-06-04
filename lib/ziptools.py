# -*- coding: utf-8 -*-

import os
import zipfile

class ziptools:

    def extract(self, file, dir, folder_to_extract="", overwrite_question=False, backup=False):
      
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)
        if not folder_to_extract:
            self._createstructure(file, dir)
        num_files = len(zf.namelist())

        for name in zf.namelist():
            if not name.endswith('/'):
                content = zf.read(name)
                name = name.replace('-master', '')
                try:
                    (path, filename) = os.path.split(os.path.join(dir, name))
                    if folder_to_extract:
                        if path != os.path.join(dir, folder_to_extract):
                            break
                    else:
                        os.makedirs(path)
                except:
                    pass

                if folder_to_extract:
                    outfilename = os.path.join(dir, filename)
                else:
                    outfilename = os.path.join(dir, name)
                try:
                    if os.path.exists(outfilename) and overwrite_question:
                        from platformcode import platformtools
                        dyesno = platformtools.dialog_yesno("Il file esiste già",
                                                            "Il file %s esiste già" \
                                                            ", vuoi sovrascrivere?" \
                                                            % os.path.basename(outfilename))
                        if not dyesno:
                            break
                        if backup:
                            import time
                            import shutil
                            hora_folder = "Copia seguridad [%s]" % time.strftime("%d-%m_%H-%M", time.localtime())
                            backup = os.path.join(get_data_path(), 'backups', hora_folder, folder_to_extract)
                            if not os.path.exists(backup):
                                os.makedirs(backup)
                            shutil.copy2(outfilename, os.path.join(backup, os.path.basename(outfilename)))
                        
                    outfile = open(outfilename, 'wb')
                    outfile.write(content)
                except:
                    pass

    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)

    def create_necessary_paths(filename):
        try:
            (path,name) = os.path.split(filename)
            os.makedirs( path)
        except:
            pass

    def _makedirs(self, directories, basedir):
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        zf = zipfile.ZipFile(file)
        dirs = []
        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name.replace('-master', ''))

        dirs.sort()
        return dirs

    def get_data_path():
        dev = xbmc.translatePath(__settings__.getAddonInfo('Profile'))

        #Crea el directorio si no existe
        if not os.path.exists(dev):
            os.makedirs(dev)

        return dev
