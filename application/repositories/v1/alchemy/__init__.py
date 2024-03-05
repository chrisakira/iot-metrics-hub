"""
Alchemy Repositories Module for Application
Version: 1.0.0
"""
from application.database.mysql_alchemy import AlchemyConnector 
from application.logging import get_logger 


class AbstractRepository:
    _MAX_ATTEMPTS = 5
     
    
    def __init__(self, logger=None, engine=None, alchemy_session=None):
        self.logger = logger if logger is not None else get_logger()
        # todo utilizar connector
        self.engine = engine if engine is not None else AlchemyConnector().get_engine()
        self.alchemy_session = alchemy_session if alchemy_session is not None else AlchemyConnector().get_session(self.engine)
        self._exception = None
        self.debug = False

    def get_new_session(self):
        return AlchemyConnector().get_session(AlchemyConnector().get_engine())
    
    def get_session(self):
        return self.session

    def get_exception(self):
        return self._exception

    def _close(self):
        self.session.close()
