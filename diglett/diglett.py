import shutil
import os
import time
import logging
import json
import string
import random
from datetime import datetime, timedelta
from service import Service
from multiprocessing.dummy import Pool as ThreadPool


def _removeEmptyFolders(path, remove_root=True):
    # Function to remove empty folders
    if not os.path.isdir(path):
        return
    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                _removeEmptyFolders(full_path)
    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and remove_root:
        os.rmdir(path)


class Config:
    _CFG_PATH = os.path.join(os.path.expanduser('~'), '.diglett')

    @staticmethod
    def get_or_create()->dict:
        """
        Generate and save or read config from config file
        time - time to sleep
        process - number copy process
        dir_format - destination directory format

        :return: dict
        """
        if os.path.isfile(Config._CFG_PATH):
            with open(Config._CFG_PATH, 'r') as f:
                config = json.load(f)
            return config
        config = {'time': 60,
                  'process': 2,
                  'working_directory': os.path.join(os.path.expanduser('~'),
                                                    'Downloads'),
                  'dir_format': '%d.%m.%y',
                  'file_types': {'doc': '', 'music': '', 'image': ''}
                  }
        with open(Config._CFG_PATH, 'w') as f:
            json.dump(config, f)
        return config


class Diglett(Service):
    def __init__(self, *args, **kwargs):
        super(Diglett, self).__init__(*args, **kwargs)
        self.logger.addHandler(logging.FileHandler('/tmp/digglet.log'))
        self.logger.setLevel(logging.DEBUG)
        self.cfg = Config.get_or_create()
        self._exts = "".join([self.cfg['file_types'][e]
                              for e in self.cfg['file_types'].keys()])

    def _check_or_create_dir(self):
        """
        check or  create today directory
        """
        # update today_dir
        date_now = datetime.now().strftime(self.cfg['dir_format'])
        self.today_dir = os.path.join(self.cfg['working_directory'], date_now)
        if not os.path.isdir(self.today_dir):
            for d in self.cfg['file_types'].keys():
                os.path.os.makedirs(os.path.join(self.today_dir, d))
                self._clear_empty_folders()

    def _clear_empty_folders(self):
        """
        Remove yesterday folder if it empty
        :return: None
        """
        date_now = datetime.today()
        yesterday = date_now - timedelta(days=1)
        yesterday = os.path.join(self.cfg['working_directory'],
                                 yesterday.strftime(self.cfg['dir_format']))
        if os.path.isdir(yesterday):
            print('Hello')
            for d in self.cfg['file_types'].keys():
                _removeEmptyFolders(os.path.join(yesterday, d))

    def _get_file_list(self)->list:
        """
        get files from working directory filtered by ext
        :return: file list
        """
        files = []

        for f in os.listdir(self.cfg['working_directory']):
            f = os.path.join(self.cfg['working_directory'], f)
            f_ext = os.path.splitext(f)[1].replace('.', '')
            if os.path.isfile(f) and f_ext != '' and f_ext in self._exts:
                files.append(f)
        return files

    def _move(self, file):
        """
        Move files to today_dir
        """
        ext = os.path.splitext(file)[1].replace('.', '').lower()
        ftype = False
        for e in self.cfg['file_types'].keys():
            if ext in self.cfg['file_types'][e]:
                ftype = e
                break
        dest = os.path.join(self.today_dir, ftype)
        try:
            shutil.move(file, dest)
        except:
            fname = os.path.splitext(os.path.basename(file))
            rnd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            dest = os.path.join(self.today_dir, ftype, fname[0]+rnd+fname[1])
            shutil.move(file, dest)

    def run(self):
        """
        Go go go
        """
        while not self.got_sigterm():
            self.logger.info("Go digg!")
            self._check_or_create_dir()
            files = self._get_file_list()
            pool = ThreadPool(self.cfg['process'])
            pool.map(self._move, files)
            pool.close()
            pool.join()
            time.sleep(self.cfg['time'])
