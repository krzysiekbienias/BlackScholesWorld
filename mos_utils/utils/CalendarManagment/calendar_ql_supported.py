import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
from scipy import stats
import QuantLib as ql
from datetime import datetime


class SetUpSchedule():
    def __init__(self, valuation_date, termination_date, calendar, business_convention, termination_business_convention,
                 date_generation, end_of_month, convention, schedule_freq):
        self._svaluation_date = valuation_date
        self._stermination_date = termination_date
        self._s_schedule_freq = schedule_freq
        self._ql_calendar = calendar
        self._s_business_convention = business_convention
        self._ql_termination_business_convention = termination_business_convention
        self._ql_date_generation = date_generation
        self._b_end_of_month = end_of_month
        self.s_days_conv = convention
        self.mdtValuationDate = self.stringIntoDateTime(s_Date=self._svaluation_date)
        self.mdtTerminationDate = self.stringIntoDateTime(s_Date=self._stermination_date)
        self.m_ql_valuation_date = self.convertDateIntoqlDate(date=self.mdtValuationDate)
        self.m_ql_termination_date = self.convertDateIntoqlDate(date=self.mdtTerminationDate)
        self.m_day_count = self.set_days_convention(give_name=self.s_days_conv)
        self.mql_period_frequency = self.set_schedule_frequency()
        self.m_schedule = self.get_schedule()
        self.ml_dates = self.get_list_of_dates()

        self.ml_yf = self.consecutive_year_fractions()  # two consecutive dates year fraction
        self.mf_yf_between_valu_date_and_maturity = self.year_fraction_between_valuation_and_maturity()



    def stringIntoDateTime(self, s_Date):
        truncateDate = s_Date[:10]
        return datetime.strptime(truncateDate, '%Y-%m-%d')

    # def convertDateIntoqlDate(self, date):
    #     if type(date) == str:
    #         year = int(date[0:4])
    #         month = int(date[5:7])
    #         day = int(date[8:])
    #         ql_date = ql.Date(day, month, year)
    #         return ql_date
    #     elif type(date) == datetime:
    #         ql_date = ql.Date(date.day, date.month, date.year)
    #         return ql_date

    def convertDateIntoqlDate(self, date):

        ql_date = ql.Date(date.day, date.month, date.year)
        return ql_date

    def set_days_convention(self, give_name):
        if (give_name == 'Actual360'):
            day_count = ql.Actual360()
            return day_count
        elif (give_name == 'Actual365'):
            day_count = ql.Actual365Fixed()
            return day_count
        elif (give_name == 'ActualActual'):
            day_count = ql.ActualActual()
            return day_count
        elif (give_name == 'Thity360'):
            day_count = ql.Thirty360()
            return day_count
        elif (give_name == 'Business252'):
            day_count = ql.Business252()
            return day_count

    def set_schedule_frequency(self):
        if self._s_schedule_freq == "Daily":
            return ql.Period(ql.Daily)
        if self._s_schedule_freq == "Weekly":
            return ql.Period(ql.Weekly)
        if self._s_schedule_freq == "Monthly":
            return ql.Period(ql.Monthly)
        if self._s_schedule_freq == "Quarterly":
            return ql.Period(ql.Quarterly)
        if self._s_schedule_freq == "Semiannual":
            return ql.Period(ql.Semiannual)
        if self._s_schedule_freq == "   ":
            return ql.Period(ql.Annual)
        if self._s_schedule_freq == "Two Dates":
            return ql.Period()

    def get_schedule(self):
        # assert isinstance(self._svaluation_date, str) or isinstance(self._svaluation_date, datetime)
        # assert isinstance(self._stermination_date, str) or isinstance(self._svaluation_date, datetime)
        return ql.Schedule(
            self.m_ql_valuation_date,
            self.m_ql_termination_date,
            self.mql_period_frequency,
            self._ql_calendar,
            self._s_business_convention,
            self._ql_termination_business_convention,
            self._ql_date_generation,
            self._b_end_of_month)

    def get_list_of_dates(self):
        return list(self.m_schedule)

    def consecutive_year_fractions(self):
        day_count = self.m_day_count
        l_yf = []
        for i in range(1, len(self.ml_dates)):
            temp = day_count.yearFraction(self.ml_dates[i - 1], self.ml_dates[i])
            l_yf.append(temp)

        return l_yf

    def year_fraction_between_valuation_and_maturity(self):
        day_count = self.m_day_count
        return day_count.yearFraction(self.ml_dates[0], self.ml_dates[-1])


class FlexibeScheduleGivingTenors:
    def __init__(self, tradeDate: str, tenors, roll_convention, callendar, convention):
        self._tradeDate = tradeDate
        self._tenors = tenors
        self._rolling_convention = roll_convention
        self._ql_calendar = callendar
        self.s_days_conv = convention

        self.m_ql_valuation_date = self.convert_string_into_ql_object(date=self._tradeDate)
        self.mSpotDate = self.setSpotDate(lag=0)
        self.mlTenorsDates = self.tenors_to_date()
        self.mSetSchedule = ql.Schedule(self.tenors_to_date(), self._ql_calendar, self._rolling_convention)
        self.m_day_count = self.set_days_convention(give_name=self.s_days_conv)
        self.ml_dates = self.get_list_of_dates()
        self.ml_yf = self.consecutive_year_fractions()  # two consecutive dates year fraction
        self.ml_yfFromSpotDate = self.fromSpotYearFraction()
        # self.mf_yf_between_valu_date_and_maturity = self.year_fraction_between_valuation_and_maturity()

    def setSpotDate(self, lag):
        return self.m_ql_valuation_date + ql.Period(lag)

    def convert_string_into_ql_object(self, date):
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[8:])
        ql_date = ql.Date(day, month, year)
        return ql_date

    def tenors_to_date(self, arguments=None):
        matur_date = []
        if arguments == None:

            for i in range(len(self._tenors)):
                if self._tenors[i][1] == 'Days':
                    temp = self.m_ql_valuation_date + ql.Period(self._tenors[i][0])
                    matur_date.append(temp)
                else:

                    temp = self.m_ql_valuation_date + ql.Period(self._tenors[i][0], self._tenors[i][1])
                    matur_date.append(temp)
        else:
            for i in range(len(arguments)):
                if arguments[i][1] == 'Days':
                    temp = self.m_ql_valuation_date + ql.Period(arguments[i][0])
                    matur_date.append(temp)
                else:

                    temp = self.m_ql_valuation_date + ql.Period(arguments[i][0], arguments[i][1])
                    matur_date.append(temp)

        return matur_date

    def get_list_of_dates(self):
        return list(self.mSetSchedule)

    def set_days_convention(self, give_name):
        if (give_name == 'Actual360'):
            day_count = ql.Actual360()
            return day_count
        elif (give_name == 'Actual365'):
            day_count = ql.Actual365Fixed()
            return day_count
        elif (give_name == 'ActualActual'):
            day_count = ql.ActualActual()
            return day_count
        elif (give_name == 'Thity360'):
            day_count = ql.Thirty360()
            return day_count
        elif (give_name == 'Business252'):
            day_count = ql.Business252()
            return day_count

    def consecutive_year_fractions(self):
        day_count = self.m_day_count
        l_yf = []
        for i in range(1, len(self.ml_dates)):
            temp = day_count.yearFraction(self.ml_dates[i - 1], self.ml_dates[i])
            l_yf.append(temp)

        return l_yf

    def fromSpotYearFraction(self):
        day_count = self.m_day_count
        l_yf = []
        for i in range(0, len(self.ml_dates)):
            temp = day_count.yearFraction(self.mSpotDate, self.ml_dates[i])
            l_yf.append(temp)
        return l_yf


if __name__ == '__main__':
    pass
