import os
import utils.logging_util as l_util
from apps.app_config import AppConfig
from utils import common_util as c_util



l_util.config()
logger=l_util.get_logger(__name__)


@c_util.time_elapsed
def main (arg_app_name):
    if arg_app_name:
        logger.info('Triggering App: {}'.format(arg_app_name))
        app_cls=AppConfig().get_app(arg_app_name)
        app_cls(**user_opts.app_params).run()

if __name__=="__main__":
    logger.info('Initializing Test Case')
    user_opts=c_util.UserOpts()
    main(user_opts.app_name)


"""
--APP_NAME=ANALYTICAL_PRICE
--APP_PARAMS
RUN_CFG=/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/mos_utils/run_cfg/black_scholes_analytic.yaml
"""

"""
--APP_NAME=EQUITY_SIMULATION
--APP_PARAMS
RUN_CFG=/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/mos_utils/run_cfg/scenario_generator_conf.yaml
"""

"""
--APP_NAME=SENSITIVITY_ANALYSIS
--APP_PARAMS
RUN_CFG=/Users/krzysiekbienias/Documents/GitHub/BlackScholesWorld/mos_utils/run_cfg/sensitivity_analysis.yaml
"""
