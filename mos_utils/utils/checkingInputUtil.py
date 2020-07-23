import os

from mos_utils.utils.ExcelUtils.excelUtils import ExcelFilesDetails,CreateDataFrame,OutputInExcel



controlPath = '/Users/krzysiekbienias/Library/Mobile Documents/com~apple~CloudDocs/Documents/GitHub/BlackScholesWorld/HelperFiles'
os.chdir(controlPath)

loadControlFile = CreateDataFrame(file_name='OptionPrice.xlsx')

dictionaryOfControlFile = loadControlFile.create_data_frame_from_excel()



