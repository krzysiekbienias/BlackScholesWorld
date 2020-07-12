import mos_utils.utils.logging_util as l_util
from mos_utils.apps.base_app import BaseApp

logger=l_util.get_logger(__name__)

def square(x):
    logger.info('lalala')
    return int(x)**2



class FunRun(BaseApp):
    def __init__(self,**app_params):
        app_name='square'
        self._x=''
        super().__init__(app_name,app_params)
    def run(self):
        square(x=self._x)




