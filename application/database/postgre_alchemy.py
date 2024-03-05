"""
SQLAlchemy Module for Application
Version: 1.0.0
"""
from time import sleep
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text, Column, Integer, String, Sequence, DateTime, func 
from sqlalchemy.orm import sessionmaker
from application.migrations.models import ExempleModel
from application.config import get_config, Configuration
from application.logging import get_logger 
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.pool import NullPool

# Definir o modelo
Base = declarative_base()

class ExempleModelBase(ExempleModel, Base):
    pass

_CONNECTION = False
_RETRY_COUNT = 0
_MAX_RETRY_ATTEMPTS = 3

def get_uri(config: Configuration = None):
    if config is None:
        config = get_config() 
    uri = 'mysql://{}:{}@{}/{}'.format(
        config.get('DB_USER'),
        config.get('DB_PASSWORD'),
        config.get('POSTGRE_DB_HOST'),
        config.get('DB'))
    return uri

def run_compatible_with_sqlalchemy():
    return psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

def reset():
    global _CONNECTION
    _CONNECTION = False
 

class AlchemyConnector:
    def __init__(self, config=None, logger=None, URI=None):
        # logger
        self.logger = logger if logger is not None else get_logger()
        # logger
        self.config = config if config is not None else get_config()
        # last_exception
        self.exception = None
        # URI
        self.URI = URI if URI is not None else get_uri()


    def get_engine(self, DATABASE_URL=None):
        try:
            if DATABASE_URL is None:
                DATABASE_URL = self.URI
            return create_engine(DATABASE_URL)
        except Exception as err:
            self.logger.error(err)
            raise err
       
    def get_session(self, engine=None):
        try:
            if engine is None:
                engine = self.get_engine()
            Session = sessionmaker(bind=engine)
            return Session()
        except Exception as err:
            self.logger.error(err)
            raise err
        
    def close_(self, session):
        try:
            session.close()
        except Exception as err:
            self.logger.error(err)
        
        
    def get_status(self):
        engine = self.get_engine()
        session = self.get_session(engine) 
        try: 
            session.execute(text('SELECT 1'))
            engine.dispose()
            return True
        except Exception as err:
            self.logger.error(err)
            engine.dispose()
            return False
        
