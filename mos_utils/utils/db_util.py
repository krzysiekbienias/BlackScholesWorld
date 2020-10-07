import pyodbc
import mos_utils.utils.common_util as c_util
import mos_utils.utils.os_util as o_util
import mos_utils.utils.logging_util as l_util
import os
import mysql.connector
import pandas as pd

curr_file_path=os.path.abspath(os.path.dirname(__file__))
logger=l_util.get_logger(__name__)

class Connection:
    def __init__(self,conn_type):
        cfg_file=os.path.join(curr_file_path,'config/db_cfg.yaml')
        cfg_obj=c_util.load_cfg('yaml',cfg_file)
        self._db_cfg=cfg_obj.get(conn_type)

    def get_conn_str(self,arg_db_name):
        ret_dict={}
        server_env=o_util.get_server_env()
        db_cfg=self._db_cfg.get(arg_db_name)
        ret_dict['db_user']=db_cfg.get('user','')
        ret_dict['db_host']=db_cfg['HOST'].get(server_env,None)
        db_name=db_cfg.get('DB_NAME','')
        if isinstance(db_name, dict):
            ret_dict['db_name']=db_name.get(server_env,None)
        else:
            ret_dict['db_name']=db_name
            conn_str=db_cfg['DRIVER_CONN_STR']
        if 'CW_ALIAS' in db_cfg:
            ret_dict['USER_ID'],ret_dict['PASSWORD']=o_util.get_unix_cred(db_cfg['CW_ALIAS'])
        else:

            credentials_file=db_cfg.get('CREDENTIALS', '')
            if os.path.exists(credentials_file):
                with open (credentials_file,'r') as f:
                    cred_info=f.read().split('::')
                    if len(cred_info)>1:
                        ret_dict['user_id']=cred_info[0]
                        ret_dict['password']=cred_info[1]
                    else:
                        raise c_util.AppException(__name__,'Credentials not in the expected format','Please have it as user_id::password in the credentials file')
            else:
                raise c_util.AppException(__name__,'Credentials File Not Found. Please configure in the yaml cfg file')
        ret_dict['db_port']=db_cfg.get('PORT','')
        logger.debug(conn_str.format(**ret_dict))
        return conn_str.format(**ret_dict)


@c_util.SingletonDecorator
class SQLConnection(Connection):
    def __init__(self,arg_db_name):
        super().__init__('SQL')
        self._db_name=arg_db_name
        self.sql_connection=self.get_sql_conn()

    def get_sql_conn(self):
        ret_connection=mysql.connector.connect(self.get_conn_str(self._db_name))
        return ret_connection

def exec_sql_query(arg_conn,sql_query):
    cr=arg_conn.cursor()
    result=cr.execute(sql_query)
    return result

def query_to_df(arg_conn,query,arg_params=None):
    df=pd.read_sql(query,arg_conn,params=arg_params)
    return df

