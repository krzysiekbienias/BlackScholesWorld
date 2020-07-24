import sys
import numpy as np
import scipy as sc
from scipy import stats
import operator
import QuantLib as ql
import seaborn as sns
import os
import matplotlib.pyplot as plt
import pandas as pd



from mos_utils.utils.CalendarManagment.calendar_ql_supported import SetUpSchedule
from mos_utils.apps.base_app import BaseApp
from mos_utils.utils.ExcelUtils.excelUtils import ExcelFilesDetails,CreateDataFrame,OutputInExcel
from mos_utils.utils.quantLibUtil import QuantLibConverter
import mos_utils.utils.logging_util as l_util



# controlPath = '/Users/krzysiekbienias/Downloads/ControlFiles'
# os.chdir(controlPath)
# controlFile = pd.read_excel('BlackScholes.xlsx', sheet_name='Input')

logger=l_util.get_logger(__name__)



class EquityModels(SetUpSchedule):

    def __init__(self, valuation_date, termination_date, calendar, convention, schedule_freq, business_convention,
                 termination_business_convention,
                 date_generation, end_of_month, type_option: str, current_price: float, strike: float,
                 ann_risk_free_rate: float,
                 ann_volatility: float, ann_dividend: float, runs: int):
        SetUpSchedule.__init__(self, valuation_date, termination_date, calendar, business_convention,
                               termination_business_convention,
                               date_generation, end_of_month, convention, schedule_freq)
        self._type_option = type_option  # call or put
        self._S0 = current_price
        self._K = strike
        self._drift = ann_risk_free_rate
        self._sigma = ann_volatility
        self._divid = ann_dividend
        self._runs = runs
        self.m_ar_equity_price = self.geometric_brownian_motion_scenario_fun()
        self.mdfprices = self.realizationPaths()
        self.mlt_payoffandST = self.calculate_payoffs()  # lt list of tuples ST and tuples and payoff sorted
        self.mf_monte_carlo_price = self.monte_carlo_price()
        self.mListOfDates = self.m_schedule
        self.mHistogST = self.histogramOfSTValues()

    def geometric_brownian_motion_scenario_fun(self):
        dt = self.ml_yf
        gbm_model = np.zeros((self._runs, len(
            self.ml_dates)))  # create empty array #TODO to nie moze byc do scenario calendar tylko zalezec od obiektu o_gbmscenarios
        gbm_model[:, 0] = self._S0  # current price
        for t in range(1, len(gbm_model[0])):
            z = np.random.standard_normal(self._runs)  # draw number from normal distribution N(0,sqrt(t*sigma))
            gbm_model[:, t] = gbm_model[:, t - 1] * np.exp(
                (self._drift - 0.5 * self._sigma ** 2) * dt[t - 1] +
                self._sigma * np.sqrt(dt[t - 1]) * z)
        return np.transpose(gbm_model)

    def calculate_payoffs(self):  # delivery_data random or given
        ST = self.m_ar_equity_price[-1]

        vpayoff = np.zeros(len(ST))
        for i in range(len(ST)):#
            if (self._type_option == 'call'):
                vpayoff[i] = max(ST[i] - self._K, 0)
            else:
                vpayoff[i] = max(self._K - ST[i], 0)
        zipped = list((zip(ST, vpayoff)))
        sorted_zip = sorted(zipped, key=lambda x: x[0])  # without sorting there is a problem with ploting
        return sorted_zip

    def monte_carlo_price(self) -> float:
        take_payoff = lambda x: x[1] #get second coordinates from tuple
        payoff = list(map(take_payoff, self.mlt_payoffandST))
        return np.mean(payoff) * np.exp(-self._drift * self.mf_yf_between_valu_date_and_maturity)

    # histogram corresponding to the final values of paths
    def plothistogramOfSt(self):
        ST = self.m_ar_equity_price[-1]
        hist = sns.distplot(ST, hist=True, rug=True)
        plt.axvline(self._S0, color='red')
        plt.xlim((0, max(ST) + 5))
        plt.xlabel("Spot Price")
        plt.show()

    def histogramOfSTValues(self):
        ST = self.m_ar_equity_price[-1]
        stHist = np.histogram(ST, bins=25)
        return stHist

    def realizationPaths(self):
        df = pd.DataFrame(self.m_ar_equity_price, index=self.ml_dates)
        return df

class ScenarioEquityRun(BaseApp):
        def __init__(self, **app_params):
            app_name = 'equity_simulation'
            """we populate input from excel"""
            self._tab_name = ''

            super().__init__(app_name, app_params)

        def run(self):
            controlPath = '/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/HelperFiles'
            os.chdir(controlPath)

            loadControlFile = CreateDataFrame(file_name='OptionPrice.xlsx')

            dictionaryOfControlFile = loadControlFile.create_data_frame_from_excel()
            controlFile = dictionaryOfControlFile[self._tab_name]

            qlConverter = QuantLibConverter(calendar=controlFile.loc[4, 'Value'])

            o_black_scholes_scenarios = EquityModels(valuation_date=controlFile.loc[0, 'Value'],
                                             termination_date=controlFile.loc[1, 'Value'],
                                              schedule_freq=controlFile.loc[2, 'Value'],
                                              convention=controlFile.loc[3, 'Value'],  # Daily,Monthly,Quarterly
                                              calendar=qlConverter.mqlCalendar,
                                              business_convention=qlConverter.mqlBusinessConvention,
                                              termination_business_convention=qlConverter.mqlTerminationBusinessConvention,
                                              date_generation=ql.DateGeneration.Forward,
                                              end_of_month=controlFile.loc[8, 'Value'],
    #                                          ##################################
                                              type_option=controlFile.loc[9, 'Value'],
                                              current_price=controlFile.loc[10, 'Value'],
                                              strike=controlFile.loc[11, 'Value'],
                                              ann_risk_free_rate=controlFile.loc[12, 'Value'],
                                              ann_volatility=controlFile.loc[13, 'Value'],
                                              ann_dividend=controlFile.loc[14, 'Value'],
                                              runs=controlFile.loc[15, 'Value'])

            logger.info(f'Monte Carlo Price is equal {o_black_scholes_scenarios.mf_monte_carlo_price}')





