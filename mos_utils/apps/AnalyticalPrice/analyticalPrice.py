import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
from scipy import stats
import operator
import QuantLib as ql
import os
import pandas as pd
import xlsxwriter

from mos_utils.utils.CalendarManagment.calendar_ql_supported import SetUpSchedule
from mos_utils.apps.base_app import BaseApp
from mos_utils.utils.ExcelUtils.excelUtils import ExcelFilesDetails,CreateDataFrame,OutputInExcel
from mos_utils.utils.quantLibUtil import QuantLibConverter
import mos_utils.utils.logging_util as l_util
from mos_utils.utils.PlotKit.plotCreator import PlotFinanceGraphs


logger=l_util.get_logger(__name__)

class Check_Arguments(ValueError):
    pass


class AnalyticBlackScholes(SetUpSchedule):
    def __init__(self, valuation_date, termination_date, calendar, convention, schedule_freq, business_convention,
                 termination_business_convention,
                 date_generation, end_of_month, type_option, current_price, strike, ann_risk_free_rate, ann_volatility,
                 ann_dividend
                 ):
        SetUpSchedule.__init__(self, valuation_date, termination_date, calendar, business_convention,
                               termination_business_convention,
                               date_generation, end_of_month, convention, schedule_freq)
        self._type_option = type_option  # call or put
        self._S0 = current_price
        self._K = strike
        self._r = ann_risk_free_rate
        self._sigma = ann_volatility
        self._divid = ann_dividend


        self.mfd1 = self.d1_fun()
        self.mfd2 = self.d2_fun()
        self.mblprice = self.black_scholes_price_fun()




    def d1_fun(self):
        d1 = (np.log(self._S0 / self._K) + (
                self._r - self._divid + 0.5 * self._sigma ** 2) * self.ml_yf[0]) / (
                     np.sqrt(self.ml_yf) * self._sigma)
        return d1

    #
    def d2_fun(self):
        d2 = (np.log(self._S0 / self._K) + (
                self._r - self._divid - 0.5 * self._sigma ** 2) * self.ml_yf[0]) / (
                     np.sqrt(self.ml_yf) * self._sigma)
        return d2

    ####################################---- Plain Vanila ----

    def black_scholes_price_fun(self):
        if (self._type_option == 'call'):
            price = self._S0 * np.exp(-self.ml_yf[0] * self._divid) * sc.stats.norm.cdf(
                self.d1_fun(), 0,
                1) - self._K * np.exp(
                -self.ml_yf[0] * self._r) * stats.norm.cdf(self.d2_fun(), 0, 1)
        else:
            price = self._K * np.exp(-self.ml_yf[0] * self._r) * stats.norm.cdf(-self.d2_fun(), 0,
                                                                                1) - self._S0 * np.exp(
                -self.ml_yf[0] * self._divid) * stats.norm.cdf(-self.d1_fun(), 0, 1)
        return price

    def digitalOption(self):
        if (self._type_option == 'call'):
            price = np.exp(-self.ml_yf[0] * self._r) * sc.stats.norm.cdf(
                self.d2_fun(), 0, 1)
        else:
            price = np.exp(-self.ml_yf[0] * self._r) * sc.stats.norm.cdf(
                -self.d2_fun(), 0, 1)
        return price

    def AssetorNothing(self):
        if (self._type_option == 'call'):
            price = self._S0 * np.exp(-self.ml_yf[0] * self._divid) * sc.stats.norm.cdf(
                self.d1_fun(), 0, 1)
        else:
            price = self._S0 * np.exp(-self.ml_yf[0] * self._divid) * sc.stats.norm.cdf(
                -self.d1_fun(), 0, 1)
        return price


##Configuration
"""
--APP_NAME=ANALYTICAL_PRICE
--APP_PARAMS
RUN_CFG=/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/mos_utils/run_cfg/black_scholes_analytic.yaml
"""



class AnalyticalRun(BaseApp):
    def __init__(self, **app_params):
        app_name='analytical_price'
        """we populate input from excel"""
        self._tab_name1=''
        self._tab_name2 =''
        self._tab_name3 =''
        self._tab_name4=''
        self._control_path=''
        super().__init__(app_name, app_params)

        #################################----Load Control File----##################################
        self.loadControlFile = CreateDataFrame(file_name='OptionPrice.xlsx',path=self._control_path)
        self.dictionaryOfControlFile = self.loadControlFile.create_data_frame_from_excel()
        #################################----Load Control File----##################################

        #################################----Load Control File for Pricing----##################################
        self.controlFilesShortMaturity = self.dictionaryOfControlFile[self._tab_name1]
        self.qlConverterSM = QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        self.controlFileMediumMaturity = self.dictionaryOfControlFile[self._tab_name2]
        self.qlConverterMM=QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        self.controlFileLongMaturity = self.dictionaryOfControlFile[self._tab_name3]
        self.qlConverterLM=QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        #################################----Load Control File for Pricing----##################################

        #################################----Load Control File for Dynamic----##################################
        self.controlPriceDynamic = self.dictionaryOfControlFile[self._tab_name4]
        self.qlConverterPriceDynamic = QuantLibConverter(calendar=self.controlPriceDynamic.loc[4, 'Value'])
        self.controlFilePriceChange = self.dictionaryOfControlFile['RANGE']['Price']
        self.controlFileVolChange = self.dictionaryOfControlFile['RANGE']['Volatility']
        #################################----Load Control File for Dynamic----##################################


    def run(self):

        o_black_scholes_short_maturity = AnalyticBlackScholes(valuation_date=self.controlFilesShortMaturity.loc[0, 'Value'],
                                                   termination_date=self.controlFilesShortMaturity.loc[1, 'Value'],
                                                   schedule_freq=self.controlFilesShortMaturity.loc[2, 'Value'],
                                                   convention=self.controlFilesShortMaturity.loc[3, 'Value'],  # Daily,Monthly,Quarterly
                                                   calendar=self.qlConverterSM.mqlCalendar,
                                                   business_convention=self.qlConverterSM.mqlBusinessConvention,
                                                   termination_business_convention=self.qlConverterSM.mqlTerminationBusinessConvention,
                                                   date_generation=ql.DateGeneration.Forward,
                                                   end_of_month=self.controlFilesShortMaturity.loc[8, 'Value'],
                                                   ##################################
                                                   type_option=self.controlFilesShortMaturity.loc[9, 'Value'],
                                                   current_price=self.controlFilesShortMaturity.loc[10, 'Value'],
                                                   strike=self.controlFilesShortMaturity.loc[11, 'Value'],
                                                   ann_risk_free_rate=self.controlFilesShortMaturity.loc[12, 'Value'],
                                                   ann_volatility=self.controlFilesShortMaturity.loc[13, 'Value'],
                                                   ann_dividend=self.controlFilesShortMaturity.loc[14, 'Value'])


        ######################################----3Month Option Setting----############################
        o_black_scholes_medium_maturity = AnalyticBlackScholes(valuation_date=self.controlFileMediumMaturity.loc[0, 'Value'],
                                                  termination_date=self.controlFileMediumMaturity.loc[1, 'Value'],
                                                  schedule_freq=self.controlFileMediumMaturity.loc[2, 'Value'],
                                                  convention=self.controlFileMediumMaturity.loc[3, 'Value'],  # Daily,Monthly,Quarterly
                                                  calendar=self.qlConverterMM.mqlCalendar,
                                                  business_convention=self.qlConverterMM.mqlBusinessConvention,
                                                  termination_business_convention=self.qlConverterMM.mqlTerminationBusinessConvention,
                                                  date_generation=ql.DateGeneration.Forward,
                                                  end_of_month=self.controlFileMediumMaturity.loc[8, 'Value'],
                                                  ##################################
                                                  type_option=self.controlFileMediumMaturity.loc[9, 'Value'],
                                                  current_price=self.controlFileMediumMaturity.loc[10, 'Value'],
                                                  strike=self.controlFileMediumMaturity.loc[11, 'Value'],
                                                  ann_risk_free_rate=self.controlFileMediumMaturity.loc[12, 'Value'],
                                                  ann_volatility=self.controlFileMediumMaturity.loc[13, 'Value'],
                                                  ann_dividend=self.controlFileMediumMaturity.loc[14, 'Value'])
        logger.info(f'We have defined one black scholes object For 3 months option')
        logger.info(f'Current Price of underlying asset = {o_black_scholes_medium_maturity._S0}.')

        logger.info(f' Annual volatility on the market is equal {o_black_scholes_medium_maturity._sigma}.')
        logger.info(f' Annual risk on the market is equal {o_black_scholes_medium_maturity._r}.')
        logger.info(f'Price is found on date {o_black_scholes_medium_maturity._svaluation_date}')
        logger.info(f'Price is found on date {o_black_scholes_medium_maturity._stermination_date}')
        logger.info(f'Annuity is calculated based on {o_black_scholes_medium_maturity.m_day_count} convention')
        logger.info(f'Year fraction for this contract is equal {o_black_scholes_medium_maturity.consecutive_year_fractions()}')
        logger.info(f' Analytical price of {o_black_scholes_medium_maturity._type_option} is equal {o_black_scholes_medium_maturity.mblprice}.')
        ######################################----3Month Option Setting----############################


        ######################################----6Month Option Setting----############################
        o_black_scholes_long_maturity = AnalyticBlackScholes(valuation_date=self.controlFileLongMaturity.loc[0, 'Value'],
                                                  termination_date=self.controlFileLongMaturity.loc[1, 'Value'],
                                                  schedule_freq=self.controlFileLongMaturity.loc[2, 'Value'],
                                                  convention=self.controlFileLongMaturity.loc[3, 'Value'],  # Daily,Monthly,Quarterly
                                                  calendar=self.qlConverterLM.mqlCalendar,
                                                  business_convention=self.qlConverterLM.mqlBusinessConvention,
                                                  termination_business_convention=self.qlConverterLM.mqlTerminationBusinessConvention,
                                                  date_generation=ql.DateGeneration.Forward,
                                                  end_of_month=self.controlFileLongMaturity.loc[8, 'Value'],
                                                  ##################################
                                                  type_option=self.controlFileLongMaturity.loc[9, 'Value'],
                                                  current_price=self.controlFileLongMaturity.loc[10, 'Value'],
                                                  strike=self.controlFileLongMaturity.loc[11, 'Value'],
                                                  ann_risk_free_rate=self.controlFileLongMaturity.loc[12, 'Value'],
                                                  ann_volatility=self.controlFileLongMaturity.loc[13, 'Value'],
                                                  ann_dividend=self.controlFileLongMaturity.loc[14, 'Value'])
        logger.info(f'We have defined one black scholes object For 3 months option')
        logger.info(f'Current Price of underlying asset = {o_black_scholes_long_maturity._S0}.')

        logger.info(f' Annual volatility on the market is equal {o_black_scholes_long_maturity._sigma}.')
        logger.info(f' Annual risk on the market is equal {o_black_scholes_long_maturity._r}.')
        logger.info(f'Price is found on date {o_black_scholes_long_maturity._svaluation_date}')
        logger.info(f'Price is found on date {o_black_scholes_long_maturity._stermination_date}')
        logger.info(f'Annuity is calculated based on {o_black_scholes_long_maturity.m_day_count} convention')
        logger.info(f'Year fraction for this contract is equal {o_black_scholes_long_maturity.consecutive_year_fractions()}')
        logger.info(f' Analytical price of {o_black_scholes_long_maturity._type_option} is equal {o_black_scholes_long_maturity.mblprice}.')

        ######################################----6Month Option Setting----############################

        prices_range = self.controlFilePriceChange.values
        vol_range = self.controlFileVolChange.values
        vol_range = vol_range[~np.isnan(vol_range)]

        changeUnderlyingPriceShortMat = [o_black_scholes_short_maturity.black_scholes_price_fun() for o_black_scholes_short_maturity._S0 in prices_range]
        change_volShortMat = [o_black_scholes_short_maturity.black_scholes_price_fun() for o_black_scholes_short_maturity._sigma in vol_range]

        changeUnderlyingPriceMediumMat = [o_black_scholes_medium_maturity.black_scholes_price_fun() for o_black_scholes_medium_maturity._S0 in prices_range]
        change_vol3m = [o_black_scholes_medium_maturity.black_scholes_price_fun() for o_black_scholes_medium_maturity._sigma in vol_range]

        changeUnderlyingPriceLongMat = [o_black_scholes_long_maturity.black_scholes_price_fun() for o_black_scholes_long_maturity._S0
                          in prices_range]
        change_vol6m = [o_black_scholes_long_maturity.black_scholes_price_fun() for o_black_scholes_long_maturity._sigma
                        in vol_range]



        #################################----EXPORTING RESULTS TO EXCEL----#########################################
        excelExport = OutputInExcel(FileName='OptionPrice.xlsx', Path=self._control_path)

        excelExport.flexibleInsertingScalar(cell_col=6, cell_row=1, value=o_black_scholes_short_maturity.mblprice[0],
                                           tab_name='INPUT_SM')

        excelExport.flexibleInsertingScalar(cell_col=6, cell_row=1, value=o_black_scholes_medium_maturity.mblprice[0],
                                           tab_name='INPUT_MM')
        excelExport.flexibleInsertingScalar(cell_col=6, cell_row=1, value=o_black_scholes_long_maturity.mblprice[0],
                                           tab_name='INPUT_LM')

        excelExport.insertRange(tab_name='RANGE',iterativeObj=changeUnderlyingPriceShortMat,colIndicator=5)
        excelExport.insertRange(tab_name='RANGE',iterativeObj=changeUnderlyingPriceMediumMat,colIndicator=6)
        excelExport.insertRange(tab_name='RANGE',iterativeObj=changeUnderlyingPriceLongMat,colIndicator=7)
        #################################----EXPORTING RESULTS TO EXCEL----#########################################

        #################################----PREPARING PLOTS----#########################################
        priceBehavior=PlotFinanceGraphs()
        priceBehavior.manyPlots(arg=prices_range,l_values=[changeUnderlyingPriceShortMat,
                                                           changeUnderlyingPriceMediumMat,
                                                           changeUnderlyingPriceLongMat],
                                                            ls_labes=['Short Maturity','Medium Maturity','Long Maturity'],
                                                            figName='Price Behaviour',
                                                            xAxisName='Equity Price',
                                                            yAxisName='Option Price',
                                                            title='Impact on Option Price')
        excelExport.insertPngFile(tab_name="RANGE",image_name='Price Behaviour',anchore='I1')
        #################################----PREPARING PLOTS----#########################################





































