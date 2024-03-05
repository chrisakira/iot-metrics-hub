"""
Device Manager for Application
Version: 1.0.0
"""
from application.config import get_config
from application.logging import get_logger
from application.services.v1.device_service import DeviceService
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException


class DeviceManager:
    def __init__(self, logger=None, config=None, device_service=None):

        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.device_service = device_service if device_service is not None else DeviceService(self.logger)

        # exception
        self.exception = None

        # debug
        self.DEBUG = None

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.device_service.debug(self.DEBUG)

    def get_device(self, request: dict):
        try: 
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
            
            data = self.device_service.get_device(request) # Query the database for file
            self.logger.debug(f"Data: {data}")
            if not data: # Could not find the record in the database
                raise DatabaseException(MessagesEnum.FIND_ERROR) # Raise an exception
            
            if self.device_service.exception: # If there was an exception
                self.exception = self.device_service.exception # Set the exception
                raise self.exception # Raise the exception
            
            if(data): 
                return data # Return the data
            else:
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR) # Raise an exception
            
        except Exception as e:
            self.exception = e
            raise e
        
    def create_device(self, request: dict):
        try:
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
            
            data = self.device_service.create_device(request)  
            
            if data is None: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            
            return data
             
        except Exception as e:
            self.exception = e
            raise e
    
    def update_device(self, request: dict):
        try:
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
            
            data = self.device_service.update_device(request)  
            
            if data is None: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            
            return data
             
        except Exception as e:
            self.exception = e
            raise e

    def delete_device(self, request: dict):
        try:
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
            
            data = self.device_service.delete_device(request)  
            
            if data is None: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            
            return data
             
        except Exception as e:
            self.exception = e
            raise e

    def list_device(self, request: dict):
        try: 
            data = self.device_service.list_device(request)  
            
            if not data: 
                raise DatabaseException(MessagesEnum.FIND_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            if(data):
                return data
            else: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)
             
        except Exception as e:
            self.exception = e
            raise e

    def ping_device(self, request: dict):
        try: 
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            data = self.device_service.ping_device(request)  
            
            if not data: 
                raise DatabaseException(MessagesEnum.FIND_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            if(data):
                return data
            else: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)
             
        except Exception as e:
            self.exception = e
            raise e

    def log_device(self, request: dict):
        try: 
            if request == {}: # If the request is empty
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            data = self.device_service.log_device(request)  
            
            if not data: 
                raise DatabaseException(MessagesEnum.FIND_ERROR)  
            
            if self.device_service.exception:  
                self.exception = self.device_service.exception 
                raise self.exception 
            if(data):
                return data
            else: 
                raise DatabaseException(MessagesEnum.UNKNOWN_ERROR)
             
        except Exception as e:
            self.exception = e
            raise e

    def list(self, request: dict):
        data = self.device_service.list(request)
        if (data is None or len(data) == 0) and self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return data

    def count(self, request: dict):
        total = self.device_service.count(request)
        if self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return total

    def get(self, request: dict, uuid):
        data = self.device_service.get(request, uuid)
        if (data is None) and self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return data

    def create(self, request: dict):
        data = self.device_service.create(request)
        if (data is None) and self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return data
 
    def update(self, request: dict, uuid):
        data = self.device_service.update(request, uuid)
        if (data is None) and self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return data

    def delete(self, request: dict, uuid):
        result = self.device_service.delete(request, uuid)
        if (result is None) and self.device_service.exception:
            self.exception = self.device_service.exception
            raise self.exception
        return result
