import logging
import logging.config
import logging.handlers
import yaml
import os
import re
from datetime import datetime

curr_file_path=os.path.abspath(os.path.dirname(__file__))

def config():
    log_cfg_file=os.path.join(curr_file_path,'config/logging_cfg.yaml')
    with open(log_cfg_file,'r') as f:
        cfg=yaml.safe_load(f.read())
        logging.config.dictConfig(cfg)

def get_logger(arg_name):
    return logging.getLogger(arg_name)

class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self,filename,file_path,max_bytes,backup_count,encoding):
        filename=filename.replace('{date}',datetime.strftime(datetime.now(),'%Y%m%d'))
        file_log_full_path=os.path.join(file_path,filename)
        super(CustomRotatingFileHandler,self).__init__(filename=file_log_full_path,maxBytes=max_bytes,
                                                       backupCount=backup_count,encoding=encoding)

class SensitiveDataFormatter(logging.Formatter):
    @staticmethod
    def _filter(s):
        return re.sub(r'(PWD|PASSWORD).*',r'PWD=*****',s)

    def format(self,record):
        original=logging.Formatter.format(self,record)
        return self._filter(original)
