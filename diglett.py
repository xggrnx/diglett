import shutil
import os
import time
import logging
import json
from datetime import datetime
from service import Service
from multiprocessing.dummy import Pool as ThreadPool


class Config:
    _CFG_PATH = os.path.join(os.path.expanduser('~'), '.diglett')

    @staticmethod
    def get_or_create() -> dict:
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
        self.logger.addHandler(logging.FileHandler('/tmp/dlc.log'))
        self.logger.setLevel(logging.DEBUG)
        self.cfg = Config.get_or_create()
        date_now = datetime.now().strftime(self.cfg['dir_format'])
        self.today_dir = os.path.join(self.cfg['working_directory'], date_now)
        self._exts = "".join([self.cfg['file_types'][e]
                              for e in self.cfg['file_types'].keys()])

    def _check_or_create_dir(self):
        """
        check or  create today directory
        """
        if not os.path.isdir(self.today_dir):
            for d in self.cfg['file_types'].keys():
                os.path.os.makedirs(os.path.join(self.today_dir, d))

    def _get_file_list(self) -> list:
        """
        get files from working directory filtered by ext
        :return: file list
        """
        files = []

        for f in os.listdir(self.cfg['working_directory']):
            f = os.path.join(self.cfg['working_directory'], f)
            if os.path.isfile(f) and os.path.splitext(f)[1].replace('.', '') in self._exts:
                files.append(f)
        return files

    def _move(self, file):
        """
        Move files to today_dir
        """
        ext = os.path.splitext(file)[1].replace('.', '')
        ftype = False
        for e in self.cfg['file_types'].keys():
            if ext in self.cfg['file_types'][e]:
                ftype = e
                break
        dest = os.path.join(self.today_dir, ftype)
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
