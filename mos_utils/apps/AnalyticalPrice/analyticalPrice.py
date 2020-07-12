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

class AnalyticalRun(BaseApp):
    def __init__(self, **app_params):
        app_name='analytical_price'
        self._tabName=''



    def run(self):
        controlPath = '/Users/krzysiekbienias/Downloads/ControlFiles'
        os.chdir(controlPath)

        loadControlFile = CreateDataFrame(file_name='OptionPrice.xlsx')

        dictionaryOfControlFile = loadControlFile.create_data_frame_from_excel()

        o_black_scholes_3m = AnalyticBlackScholes(valuation_date=controlFile3m.loc[0, 'Value'],
                                                  termination_date=controlFile3m.loc[1, 'Value'],
                                                  schedule_freq=controlFile3m.loc[2, 'Value'],
                                                  convention=controlFile3m.loc[3, 'Value'],  # Daily,Monthly,Quarterly
                                                  calendar=qlConverter.mqlCalendar,
                                                  business_convention=qlConverter.mqlBusinessConvention,
                                                  termination_business_convention=qlConverter.mqlTerminationBusinessConvention,
                                                  date_generation=ql.DateGeneration.Forward,
                                                  end_of_month=controlFile3m.loc[8, 'Value'],
                                                  ##################################
                                                  type_option=controlFile3m.loc[9, 'Value'],
                                                  current_price=controlFile3m.loc[10, 'Value'],
                                                  strike=controlFile3m.loc[11, 'Value'],
                                                  ann_risk_free_rate=controlFile3m.loc[12, 'Value'],
                                                  ann_volatility=controlFile3m.loc[13, 'Value'],
                                                  ann_dividend=controlFile3m.loc[14, 'Value'])
                                                )











