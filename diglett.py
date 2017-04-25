import os
import time
import logging
import json
from datetime import datetime
from service import Service

class Config:
    _CFG_PATH = os.path.join(os.path.expanduser('~'), '.diglett')

    @staticmethod
    def get_or_create() -> json:
        """

        :return: 
        """
        if os.path.isfile(Config._CFG_PATH):
            with open(Config._CFG_PATH, 'r') as f:
                config = json.load(f)
            return config
        config = {'time': '60',
                  'working_directory': os.path.join(os.path.expanduser('~'), 'Downloads'),
                  'dir_format': '%d.%m.%y',
                  'file_types': {"doc": "", 'music': "", 'image': ""}
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
        self.now_dir = os.path.join(self.cfg['working_directory'], date_now)

    def check_or_create_dir(self):
        """
        :return: 
        """
        if not os.path.isdir(self.now_dir):
            for d in self.cfg['file_types'].keys():
                os.path.os.makedirs(os.path.join(self.now_dir, d))

    def get_file_list(self):
        """

        :return: 
        """
        #files = [f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]
        pass


    def run(self):
        """
        Go go go
        :return: 
        """
        while not self.got_sigterm():
            self.logger.info("Go digg!111")
            self.check_or_create_dir()
            time.sleep(5)