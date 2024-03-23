"""
Data Manager for Application
Version: 1.0.0
"""
from application.config import get_config
from application.logging import get_logger
from application.services.v1.data_service import DataService
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException 


class DataManager:
    def __init__(self, logger=None, config=None, data_service=None):

        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.data_service = data_service if data_service is not None else DataService(self.logger)

        # exception
        self.exception = None

        # debug
        self.DEBUG = None

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.data_service.debug(self.DEBUG)
 
    def receive_file(self, file, headers):
        data = self.data_service.receive_file(file, headers)
        if (data is None) or self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data
 
 
    def process_MF4(self, file, headers):
        data = self.data_service.process_MF4(file, headers)
        if self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data
 
 
 
 
 
    def list(self, request: dict):
        data = self.data_service.list(request)
        if (data is None or len(data) == 0) and self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data

    def count(self, request: dict):
        total = self.data_service.count(request)
        if self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return total

    def get(self, request: dict, uuid):
        data = self.data_service.get(request, uuid)
        if (data is None) and self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data

    def create(self, request: dict):
        data = self.data_service.create(request)
        if (data is None) and self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data
 
    def update(self, request: dict, uuid):
        data = self.data_service.update(request, uuid)
        if (data is None) and self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return data

    def delete(self, request: dict, uuid):
        result = self.data_service.delete(request, uuid)
        if (result is None) and self.data_service.exception:
            self.exception = self.data_service.exception
            raise self.exception
        return result
