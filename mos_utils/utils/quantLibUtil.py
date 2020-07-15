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


class QuantLibConverter:
    def __init__(self, calendar):
        self._calendar = calendar
        self.mqlCalendar = self.setCalendar()
        self.mqlBusinessConvention = self.setBusinessConvention()
        self.mqlTerminationBusinessConvention = self.setTerminationBusinessConvention()
        self.mqlDateGeneration = self.setWayOfDateGeneration()

    def setCalendar(self):
        if self._calendar == 'USA':
            return ql.UnitedStates()
        if self._calendar == 'United Kingdom':
            return ql.UnitedKingdom()
        if self._calendar == 'Switzerland':
            return ql.Switzerland()
        if self._calendar == 'Poland':
            return ql.Poland()

    def setBusinessConvention(self):
        return ql.Following

    def setTerminationBusinessConvention(self):
        return ql.Following

    def setWayOfDateGeneration(self):
        return ql.DateGeneration.Forward