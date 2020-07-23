import os
from abc import ABCMeta,abstractmethod

import utils.common_util as c_util

curr_file_path=os.path.abspath(os.path.dirname(__file__))

class BaseApp:
    __metaclass__=ABCMeta

    def __init__(self,arg_app_name,arg_app_params):
        self._app=arg_app_name

        #Adding App Params as attributes
        self.__dict__.update(arg_app_params)

        #Only load config file if both the attribs are present
        if hasattr(self,'_cfg_type') and hasattr(self,'_cfg_file'):
            self._app_cfg=c_util.load_cfg(self._cfg_type,self._cfg_file)
        if hasattr(self,'_run_cfg'):
            self._run_cfg=c_util.load_cfg('yaml',self._run_cfg,yaml_load_type='normal_load')
            run_cfg_dict=c_util.rename_keys_lowercase(self._run_cfg)
            self.__dict__.update(run_cfg_dict)

    @abstractmethod
    def run(self):
        pass

    def hasattr(self,attr_name):
        return attr_name in self.__dict__