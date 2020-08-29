import argparse
import os
import re
import time
import yaml

import utils.logging_util as l_util
logger=l_util.get_logger(__name__)


class SingletonDecorator:
    def __init__(self,arg_class):
        self._cls=arg_class
        self.instance=None

    def __call__(self,*args,**kwargs):
        if not self.instance:
            self.instance=self._cls(*args,**kwargs)
        return self.instance


class StoreDictKeyPair(argparse.Action):
    def __init__(self,option_strings,dest,nargs=None,**kwargs):
        self._nargs=nargs
        super(StoreDictKeyPair,self).__init__(option_strings,dest,nargs=nargs,**kwargs)

    def __call__(self,parser,namespace,values,option_string=None):
        my_dict={}
        logger.info('APP_PARAMS: {}'.format(values))
        for kv in values:
            k,v=kv.split("=")
            #setting keys with _name so can be used as instance variables later in the code
            my_dict['_'+k.lower()]=v
        setattr(namespace,self.dest,my_dict)

def setup_arg_parser():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--APP_NAME',
                        action='store',
                        dest='appName',
                        required=True,
                        help='App Name to Invoke')

    parser.add_argument("--APP_PARAMS",dest='appParams',action=StoreDictKeyPair,nargs="+",metavar="KEY=VAL")
    return parser


@SingletonDecorator
class UserOpts:
    def __init__(self):


        self.cmd_parser=setup_arg_parser()
        self.cmd_opts=self.cmd_parser.parse_args()
        self.app_name=self.cmd_opts.appName
        self.app_params=self.cmd_opts.appParams

def time_elapsed(arg_func):
    def exec_time(*args,**kwargs):
        t0=time.time()
        arg_func(*args,**kwargs)
        t1=time.time()
        logger.info('Time taken to complete app {0}:::{1}'.format(args[0],t1-t0))
    return exec_time


class AppException(Exception):

    def __init__(self,exception_source,message,additional_info=None):
        self.exception_source=exception_source
        self.message=message
        self.additional_info=additional_info
        super(AppException, self).__init__(message)

def load_cfg(arg_cfg_type,arg_cfg_file,yaml_loader=yaml.BaseLoader,yaml_load_type='safe_load'):
    cfg_obj=None
    if os.path.exists(arg_cfg_file):
        if arg_cfg_type=='yaml':
            with open(arg_cfg_file,mode='r') as f:
                if yaml_load_type=='safe_load':
                    cfg_obj=yaml.safe_load(f)
                else:
                    cfg_obj=yaml.load(f,Loader=yaml_loader)
        else:
            error_msg='Config type ::{0} not supported. Only .yaml are supported'.format(arg_cfg_type)
            logger.error(error_msg)
            raise AppException(__name__,error_msg)
    else:
        logger.error('Config File ::{0} not found!'.format(arg_cfg_file))
    return cfg_obj


def get_date_from_file_name(arg_file_name):
    search_pat=r'\d{6,8}'
    date_str=re.search(search_pat,arg_file_name)
    if date_str:
        return date_str.group()
    else:
        logger.error('Not able to find date in the file ::{0}!'.format(arg_file_name))
        return ''

def str_to_bool(arg_val):
    if arg_val:
        return arg_val.lowe() in ['yes','y','1','true']
    return False

def evaluate_sql(sql_file,param_dict):
    ret_query=''
    with open(sql_file,model='r') as f:
        ret_query=f.read()
        if param_dict:
            ret_query=ret_query.replace('--','')
            ret_query=ret_query.format(**param_dict)
    return ret_query

def rename_keys_lowercase(arg_dict:dict):
    keys_list=[f'_{x.lower()}' for x in arg_dict.keys()]
    return dict(zip(keys_list,list(arg_dict.values())))





