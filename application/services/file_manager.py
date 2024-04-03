"""
File Manager for Application
Version: 1.0.0
"""
from application.config import get_config
from application.logging import get_logger
from application.services.v1.file_service import FileService
from application.services.v1.device_service import DeviceService
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException 


class FileManager:
    def __init__(self, logger=None, config=None, file_service=None):

        self.logger = logger if logger is not None else get_logger()
        # configurations
        self.config = config if config is not None else get_config()
        # service
        self.file_service = file_service if file_service is not None else FileService(self.logger)

        # exception
        self.exception = None

        # debug
        self.DEBUG = None

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.file_service.debug(self.DEBUG)
 
    def post_file(self, file, request: dict):   
        device_service = DeviceService(self.logger)
        result = device_service.get_device({'mac_address': request['mac_address']})
        if result is None:
            error = DatabaseException(MessagesEnum.FIND_ERROR)
            error.params = 'Device not found' 
            self.exception = error
            raise self.exception
        
        data = self.file_service.post_file(file, request)
        if self.file_service.exception:
            self.exception = self.file_service.exception
            raise self.exception
        return data
    
    def get_file(self, request: dict):   
        data = self.file_service.get_file(request)
        if self.file_service.exception:
            self.exception = self.file_service.exception
            raise self.exception
        return data
    