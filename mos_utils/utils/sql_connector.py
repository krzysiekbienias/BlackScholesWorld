import mysql.connector
import numpy as np
import pandas as pd
import pymysql
import sqlalchemy
from os import listdir
import os
from typing import List
from six import string_types

from mos_utils.utils.common_util import load_cfg

curr_file_path=os.path.abspath(os.path.dirname(__file__))


class SQLConnector:
    def __init__(self):
        self.m_connection_details = self.set_connection_details()
        self.m_db_cursor = self.m_connection_details.cursor()
        # self.mdf_from_query = self.execute_query()
        self.engine = sqlalchemy.create_engine('mysql+pymysql://root:Numeraire2019@127.0.0.1:3306/sql_store')
        #self.df = self.testQuery(date='2014-05-19')

    def load_db_cfg(self):
        cfg_file=os.path.join(curr_file_path,'db_cfg.yaml')
        self.db_cfg=load_cfg('yaml',cfg_file)
        credentials_file=self.db_cfg.get('CREDENTIALS','')
        if os.path.exists(credentials_file):
            with open(credentials_file,'r') as f:
                cred_info=f.read().split('::')
                if cred_info>1:
                    self.db_cfg['USER_ID']=cred_info[0]
                    self.db_cfg['PASSWORD']=cred_info[1]
                else:
                    raise Exception('Credentials not in the expected.'\
                                    'Please have it as user_id::password in the credentils file')
        else:
            raise Exception('Credentils file not found. Please configure in the yaml cfg file')



    def set_connection_details(self):
        return mysql.connector.connect(host=self.db_cfg['HOST'],
                                       user=self.db_cfg['USER_ID'],
                                       passwd=self.db_cfg['PASSWORD'],
                                       database='DB_NAME')

    def quote_sql_string(self, value):
        '''
        If `value` is a string type, escapes single quotes in the string
        and returns the string enclosed in single quotes.
        '''
        if isinstance(value, string_types):
            new_value = str(value)
            new_value = new_value.replace("'", "''")
            return "'{}'".format(new_value)
        return value

    def testQuery(self, date=None):  # example of dynamic query with fstrings
        query = f'''SELECT * FROM sql_store.usd3mlibor
                where observation_date='{date}' '''
        df = pd.read_sql(query, con=self.m_connection_details)
        return df

    def export_data_frame(self, data_frame: pd.DataFrame, table_name: str):
        return data_frame.to_sql(name=table_name, con=self.engine, index=True, if_exists='append')

    def close_conection(self):
        self.m_connection_details.close()


def load_cfg

if __name__ == "__main__":
    pass
