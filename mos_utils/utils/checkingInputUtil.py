import os

from mos_utils.utils.ExcelUtils.excelUtils import ExcelFilesDetails,CreateDataFrame,OutputInExcel
from mos_utils.apps.base_app import BaseApp
import mos_utils.utils.logging_util as l_util

logger=l_util.get_logger(__name__)
#Configuration
"""
--APP_NAME=CHECK_INPUT
--APP_PARAMS
TAB_NAME=
FILE_DIRECTORY=/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/HelperFiles
FILE_NAME=OptionPrice.xlsx
"""

class CheckInputRun(BaseApp):
    def __init__(self, **app_params):
        app_name='check_input'
        """we populate input from excel"""
        self._tab_name=''
        self._file_directory=''
        self._file_name=''
        super().__init__(app_name, app_params)
        self.paramDict = self.convertToDict()

    def convertToDict(self):
        controlPath = self._file_directory
        os.chdir(controlPath)

        loadInputFiles = CreateDataFrame(file_name=self._file_name)

        dfOfInput = loadInputFiles.create_data_frame_from_excel()
        dfOfInput.to_dict()




    def run(self):


        logger.info("Check input parameters")










