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

