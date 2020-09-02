import os

from mos_utils.apps.AnalyticalPrice.analyticalPrice import AnalyticalRun
from mos_utils.utils.checkingInputUtil import CheckInputRun
from mos_utils.apps.MonteCarloSimulation.scenario_generator import ScenarioEquityRun
from mos_utils.apps.Greeks.greeks import GreeksRun


curr_file_path=os.path.abspath(os.path.dirname(__file__))

class AppConfig:
    "A Factory Class to dispatch the required App based on its name"

    app_config_dict=dict()

    def __init__(self):
        self.app_config_dict['ANALYTICAL_PRICE']=AnalyticalRun
        self.app_config_dict['CHECK_INPUT']=CheckInputRun
        self.app_config_dict['EQUITY_SIMULATION']=ScenarioEquityRun
        self.app_config_dict['SENSITIVITY_ANALYSIS']=GreeksRun

    def get_app(self,arg_app_name):
        """Returns the app based on the name
        Arguments:
            arg_app_name {}
        Returns:
              [BaseApp]--[Corresponding App's class]

        """

        if arg_app_name in self.app_config_dict.keys():
            return self.app_config_dict[arg_app_name]
        else:
            raise AppException(__name__,f'App Name::{arg_app_name} is not defined. Please pass correct App Name.')