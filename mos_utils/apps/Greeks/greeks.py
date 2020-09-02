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
from mos_utils.apps.AnalyticalPrice.analyticalPrice import AnalyticBlackScholes
from mos_utils.utils.PlotKit.plotCreator import PlotFinanceGraphs

logger=l_util.get_logger(__name__)

class Check_Arguments(ValueError):
    pass



class GreeksParameters(AnalyticBlackScholes):
    def __init__(self, valuation_date, termination_date, calendar, convention, schedule_freq,
                 business_convention,
                 termination_business_convention,
                 date_generation, end_of_month, type_option, current_price, strike,
                 ann_risk_free_rate,
                 ann_volatility,
                 ann_dividend
                 ):

        AnalyticBlackScholes.__init__(self, valuation_date, termination_date, calendar, convention, schedule_freq,
                                      business_convention,
                                      termination_business_convention,
                                      date_generation, end_of_month, type_option, current_price, strike,
                                      ann_risk_free_rate,
                                      ann_volatility,
                                      ann_dividend,
                                      )

        self.m_delta = self.delta()
        self.m_gamma = self.gamma()
        self.m_vega = self.vega()

    def delta(self):

        if (self._type_option == 'call'):
            delta = stats.norm.cdf(self.d1_fun(), 0, 1)

        else:
            delta = -stats.norm.cdf(-self.d1_fun(), 0, 1)

        return delta

    def gamma(self):  # for call and put is identical
        gamma = stats.norm.pdf(self.d1_fun(), 0, 1) * np.exp(
            -self._divid * self.mf_yf_between_valu_date_and_maturity) / (
                        self._S0 * self._sigma * np.sqrt(
                    self.mf_yf_between_valu_date_and_maturity))

        return gamma

    def vega(self):
        vega = self._S0 * np.exp(-self._divid * self.mf_yf_between_valu_date_and_maturity) * np.sqrt(
            self.mf_yf_between_valu_date_and_maturity) * stats.norm.pdf(self.d1_fun(), 0, 1)

        return vega

    def theta(self):
        if (self._type_option == 'call'):
            fTheta = -self._S0 * stats.norm.pdf(self.d1_fun(), 0, 1) * self._sigma * np.exp(
                -self._divid * self.mf_yf_between_valu_date_and_maturity) / 2 * np.sqrt(
                self.mf_yf_between_valu_date_and_maturity) + self._divid * self._S0 * np.exp(
                -self._divid *
                self.mf_yf_between_valu_date_and_maturity) * stats.norm.pdf(self.d1_fun(), 0,
                                                                            1) - self._r * self._K * np.exp(-self._r *
                                                                                                            self.mf_yf_between_valu_date_and_maturity) * stats.norm.pdf(
                self.d2_fun(), 0, 1)
        if (self._type_option == 'put'):
            fTheta = -self._S0 * stats.norm.pdf(self.d1_fun(), 0, 1) * self._sigma * np.exp(
                -self._divid * self.mf_yf_between_valu_date_and_maturity) / 2 * np.sqrt(
                self.mf_yf_between_valu_date_and_maturity) - self._divid * self._S0 * np.exp(
                -self._divid *
                self.mf_yf_between_valu_date_and_maturity) * stats.norm.pdf(-self.d1_fun(), 0,
                                                                            1) - self._r * self._K * np.exp(-self._r *
                                                                                                            self.mf_yf_between_valu_date_and_maturity) * stats.norm.pdf(
                -self.d2_fun(), 0, 1)
        return fTheta


class GreeksRun(BaseApp):
    def __init__(self,**app_params):
        app_name='sensitivity_analysis'
        self._tab_name1 = ''
        self._tab_name2 = ''
        self._tab_name3 = ''

        self._control_path = ''
        self._file_name=''
        super().__init__(app_name, app_params)

        #################################----Load Control File----##################################
        self.loadControlFile = CreateDataFrame(file_name=self._file_name, path=self._control_path)
        self.dictionaryOfControlFile = self.loadControlFile.create_data_frame_from_excel()
        #################################----Load Control File----##################################

        #################################----Load Control File for Pricing----##################################
        self.controlFilesShortMaturity = self.dictionaryOfControlFile[self._tab_name1]
        self.qlConverterSM = QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        self.controlFileMediumMaturity = self.dictionaryOfControlFile[self._tab_name2]
        self.qlConverterMM = QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        self.controlFileLongMaturity = self.dictionaryOfControlFile[self._tab_name3]
        self.qlConverterLM = QuantLibConverter(calendar=self.controlFilesShortMaturity.loc[4, 'Value'])
        #################################----Load Control File for Pricing----##################################

        self.controlFilePriceChange = self.dictionaryOfControlFile['RANGE']['Price']
        self.controlFileVolChange = self.dictionaryOfControlFile['RANGE']['Volatility']

    def run(self):
        greeks_sm = GreeksParameters(valuation_date=self.controlFilesShortMaturity.loc[0, 'Value'],
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

        logger.info('Create Greeks Object for Short Maturity Contract Completed')

        greeks_mm = GreeksParameters(valuation_date=self.controlFileMediumMaturity.loc[0, 'Value'],
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

        logger.info('Create Greeks Object for Medium Maturity Contract Completed')

        greeks_lm = GreeksParameters(valuation_date=self.controlFileLongMaturity.loc[0, 'Value'],
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

        logger.info('Create Greeks Object for Long Maturity Contract Completed')

        prices_range = self.controlFilePriceChange.values
        vol_range = self.controlFileVolChange.values

        deltaShortMaturChanheWRTSandT=[greeks_sm.delta() for greeks_sm._S0 in prices_range]
        deltaMediumMaturChanheWRTSandT=[greeks_mm.delta() for greeks_mm._S0 in prices_range]
        deltaLongMaturChanheWRTSandT=[greeks_lm.delta() for greeks_lm._S0 in prices_range]

        excelExport = OutputInExcel(FileName=self._file_name, Path=self._control_path)
        logger.info('Insert Delta of short matirity contract to excel File')
        excelExport.flexibleInsertingScalar(cell_col=6, cell_row=1, value=greeks_sm.m_delta[0],
                                            tab_name=self._tab_name1)



