import logging, pathlib
from datetime import datetime


class Logger:
    def __init__(self, level=logging.INFO):
        # create required folders
        log_folder = 'log'
        self.create_folder(log_folder)
        self.create_folder('audio_recording')
        self.create_folder('screens')
        # config logger
        file_path = f'{log_folder}/{datetime.today().strftime("%Y-%m-%d")}.txt'
        log_format = '[%(asctime)s] [%(levelname)5s] %(message)s'
        logging.basicConfig(filename=file_path, encoding='utf-8', format=log_format, datefmt='%Y-%m-%d %H:%M:%S', level=level)

        self.logger = logging.getLogger()

    @staticmethod
    def create_folder(folder_name):
        pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)

