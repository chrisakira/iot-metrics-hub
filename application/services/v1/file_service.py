"""
File Service for Application
Version: 1.0.0
"""
import copy

from datetime import datetime
from application import helper
from application.database.mysql_alchemy import AlchemyConnector
from application.database.redis import RedisConnector
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException, ServiceException
from application.filter_helper import filter_xss_injection
from application.helper import get_function_name
from application.logging import get_logger
from application.repositories.v1.alchemy.file_repository import FileRepository as AlchemyFileRepository
from application.repositories.v1.redis.file_repository import FileRepository as RedisDataRepository
from application.vos.file import FileVO
from io import BytesIO
import pytz
import struct
import io
import ast

class FileService:
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, alchemy_session=None, redis_connector=None, 
                redis_file_repository=None, alchemy_file_repository=None):
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection        
        self.alchemy_session = alchemy_session if alchemy_session is not None else AlchemyConnector()
        
        # todo passar apenas connector
        # mysql repository
        
        self.alchemy_file_repository = alchemy_file_repository if alchemy_file_repository is not None \
            else AlchemyFileRepository(alchemy_session=self.alchemy_session.get_session(self.alchemy_session.get_engine()))

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()
            # todo passar apenas connector
            # redis repository
            self.redis_file_repository = redis_file_repository if redis_file_repository is not None \
                else RedisDataRepository(redis_connection=self.redis_connector.get_connection())

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.alchemy_file_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_file_repository.debug = self.DEBUG
                
    def post_file(self, file, request): 
        List_required_fields=["mac_address"]
          
        if request == dict():
            error = ValidationException(MessagesEnum.REQUEST_ERROR)
            error.params = "Request is empty"
            self.exception = error
            raise self.exception
            
        file_vo = FileVO(request)
        for required_fields in List_required_fields: 
            if required_fields not in file_vo.__dict__:
                error = ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
                error.params = required_fields
                self.exception = error
                raise self.exception
            
        if "created_at" not in file_vo.__dict__:
            file_vo.created_at = datetime.now(pytz.utc)
        else:
            file_vo.created_at = datetime.fromtimestamp(file_vo.created_at, pytz.utc)	
        
        file_vo.name = file.filename
        file_vo.file_type = file.filename.split(".")[-1]
        file_vo.file_size = len(file.read())
        file.seek(0)
        self.alchemy_file_repository.create(file_vo, file = file.read())
        if self.alchemy_file_repository._exception:
            self.exception = self.alchemy_file_repository._exception
            raise self.exception
        
        return True     
               
    def get_file(self, file, request): 
        List_required_fields=["name", "id"]
          
        if request == dict():
            error = ValidationException(MessagesEnum.REQUEST_ERROR)
            error.params = "Request is empty"
            self.exception = error
            raise self.exception
            
        file_vo = FileVO(request)
        found = False
        key =  None
        value  = None
        for required_fields in List_required_fields: 
            if required_fields in file_vo.__dict__:
                found = True
                
        if found == False:
            error = ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            error.params = required_fields
            self.exception = error
            raise self.exception
        
        result = self.alchemy_file_repository.get(["file", "name"], file_vo)
        if self.alchemy_file_repository._exception:
            self.exception = self.alchemy_file_repository._exception
            raise self.exception
        
        return result     
    