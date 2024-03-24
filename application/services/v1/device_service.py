"""
Device Service for Application
Version: 1.0.0
"""
import copy

from datetime import datetime
from application import helper
from application.database.mysql_alchemy import AlchemyConnector
from application.database.mysql import MySQLConnector
from application.database.redis import RedisConnector
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException, ServiceException
from application.filter_helper import filter_xss_injection
from application.helper import get_function_name
from application.logging import get_logger
from application.repositories.v1.alchemy.device_repository import DeviceRepository as AlchemyDeviceRepository
from application.repositories.v1.mysql.device_repository import DeviceRepository as MysqlDeviceRepository
from application.repositories.v1.redis.device_repository import DeviceRepository as RedisDeviceRepository
from application.vos.device import DeviceVO
import pytz


class DeviceService:
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, alchemy_session=None, redis_connector=None, device_repository=None,
                redis_device_repository=None, alchemy_device_repository=None):
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        
        self.alchemy_session = alchemy_session if alchemy_session is not None else AlchemyConnector()
        # todo passar apenas connector
        # mysql repository
        self.device_repository = device_repository if device_repository is not None \
            else MysqlDeviceRepository(mysql_connection=self.mysql_connector.get_connection())

        self.alchemy_device_repository = alchemy_device_repository if alchemy_device_repository is not None \
            else AlchemyDeviceRepository(alchemy_session=self.alchemy_session.get_session(self.alchemy_session.get_engine()))

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()
            # todo passar apenas connector
            # redis repository
            self.redis_device_repository = redis_device_repository if redis_device_repository is not None \
                else RedisDeviceRepository(redis_connection=self.redis_connector.get_connection())

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.device_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_device_repository.debug = self.DEBUG

    def list_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try:
            device_vo = DeviceVO(request)
            if request != {}:
                found = False 
                for required_field in required_fields: 
                    if required_field in device_vo.__dict__:
                        found = True
                        if device_vo.__dict__[required_field] == "":
                            raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
                        
                if found == False:
                    raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)  

            result =  self.alchemy_device_repository.list([  "id", 
                                                    "name",
                                                    "mac_address",
                                                    "description",
                                                    "active",
                                                    "status",
                                                    "model",
                                                    "firmware",
                                                    "last_seen",
                                                    "created_at",
                                                    "updated_at",
                                                    "deleted_at",
                                                    "delete_status"],device_vo)	 
            self.logger.info('method: {} - result: {}'.format(get_function_name(), result))
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            return result
            
        except Exception as e:
            self.exception = e
            raise e
    
    def get_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try:
            device_vo = DeviceVO(request)
            found = False 
            for required_field in required_fields: 
                if required_field in device_vo.__dict__:
                    found = True
                    if device_vo.__dict__[required_field] == "":
                        raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
                    
            if found == False:
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)  

            result =  self.alchemy_device_repository.get([  "id", 
                                                    "name",
                                                    "mac_address",
                                                    "description",
                                                    "active",
                                                    "status",
                                                    "model",
                                                    "firmware",
                                                    "last_seen",
                                                    "created_at",
                                                    "updated_at",
                                                    "deleted_at",
                                                    "delete_status"],device_vo)	 
            self.logger.info('method: {} - result: {}'.format(get_function_name(), result))
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            return result
            
        except Exception as e:
            self.exception = e
            raise e
    
    def create_device(self, request: dict):
        required_fields = ["name", "mac_address", "description", "active", "status", "model", "firmware"] 
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try:
            device_vo = DeviceVO(request)
            
            for required_field in required_fields: 
                if required_field not in device_vo.__dict__:
                    raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
            
            if 'created_at' not in device_vo.__dict__:
                device_vo.created_at = datetime.now()
                
            result =  self.alchemy_device_repository.create(device_vo)	 
            
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            if result == True: 
                return device_vo
            
        except Exception as e:
            self.exception = e
            raise e

    def update_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try:
            device_vo = DeviceVO(request)
            found = False
            key = None
            value = None
            for required_field in required_fields: 
                if required_field in device_vo.__dict__:
                    found = True
                    key = required_field
                    value = device_vo.__dict__[required_field]
            if found == False:        
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
             
            result =  self.alchemy_device_repository.update(device_vo, value=value, key=key) 		 
            
            if result == None:
                raise ValidationException(MessagesEnum.UNKNOWN_ERROR)
                        
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            if result == True: 
                return device_vo
            
        except Exception as e:
            self.exception = e
            raise e

    def delete_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try:
            device_vo = DeviceVO(request)
            found = False
            key = None
            value = None
            for required_field in required_fields: 
                if required_field in device_vo.__dict__:
                    found = True
                    key = required_field
                    value = device_vo.__dict__[required_field]
            if found == False:        
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR) 
             
            result =  self.alchemy_device_repository.delete(device_vo, value=value, key=key) 		 
            
            if result == None:
                raise ValidationException(MessagesEnum.UNKNOWN_ERROR)
                        
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            if result == True: 
                return device_vo
            
        except Exception as e:
            self.exception = e
            raise e
    
    def list_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try: 
            device_vo = DeviceVO(request) 
            found = True
            if request != {}:
                found = False               
                for required_field in required_fields:
                    if required_field in device_vo.__dict__:
                        found = True 
            if found == False:                     
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            
            result =  self.alchemy_device_repository.list([  "id", 
                                                    "name",
                                                    "mac_address",
                                                    "description",
                                                    "active",
                                                    "status",
                                                    "model",
                                                    "firmware",
                                                    "last_seen",
                                                    "created_at",
                                                    "updated_at",
                                                    "deleted_at",
                                                    "delete_status"],device_vo)	 
            self.logger.info('method: {} - result: {}'.format(get_function_name(), result))
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            return result
            
        except Exception as e:
            self.exception = e
            raise e
    
    def ping_device(self, request: dict):
        required_fields = ["name", "mac_address"] 
        
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try: 
            device_vo = DeviceVO(request) 
            key = None
            value = None
            found = False               
            for required_field in required_fields:
                if required_field in device_vo.__dict__:
                    found = True 
                    key = required_field
                    value = device_vo.__dict__[required_field]
            if found == False:                     
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            
            result =  self.alchemy_device_repository.ping(key=key, value=value)	 
            
            self.logger.info('method: {} - result: {}'.format(get_function_name(), result))
            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            return result
            
        except Exception as e:
            self.exception = e
            raise e
    
    def log_device(self, request: dict):
        required_fields_device = ["name", "mac_address"] 
        required_fields_log = ["type","message"] 
        
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        try: 
            device_log = DeviceVO(request) 
            key = None
            value = None
            found = False               
            for required_field in required_fields_device:
                if required_field in device_log.__dict__:
                    found = True 
                    key = required_field
                    value = device_log.__dict__[required_field]
     
            found = False               
            for required_field in required_fields_log:
                if required_field in device_log.__dict__:
                    found = True 
     
            if found == False:                     
                raise ValidationException(MessagesEnum.PARAM_REQUIRED_ERROR)
            device = DeviceVO()
            device.__dict__[key] = value 
            device_id = self.alchemy_device_repository.get(["id"], device)
            if device_id == None:
                raise ValidationException(MessagesEnum.FIND_ERROR)

            for required_field in required_fields_device:
                if required_field in device_log.__dict__:
                    del device_log.__dict__[required_field] 
            device_log.device_id = device_id["id"]
            result =  self.alchemy_device_repository.log_error(device_log)	 

            if self.alchemy_device_repository._exception:
                self.exception = self.alchemy_device_repository._exception
                raise self.exception

            return result
            
        except Exception as e:
            self.exception = e
            raise e
    
################## Default operations ##################
    def list(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        data = []
        where = request['where']
        if where == dict():
            where = {
                'active': 1
            }

        # exclude deleted
        where['deleted_at'] = None

        try:
            offset = request['offset']
            limit = request['limit']
            order_by = request['order_by']
            sort_by = request['sort_by']
            fields = request['fields']
            data = self.device_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields)

            # convert to vo and prepare for api response
            if data:
                vo_data = []
                for item in data:
                    vo_data.append(DeviceVO(item, default_values=False).to_api_response())
                data = vo_data

            # set exception if it happens
            if self.device_repository.get_exception():
                raise DatabaseException(MessagesEnum.LIST_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def count(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        total = 0
        where = request['where']
        if where == dict():
            where = {
                'active': 1
            }

        # exclude deleted
        where['deleted_at'] = None

        try:
            order_by = request['order_by']
            sort_by = request['sort_by']
            total = self.device_repository.count(
                where=where, order_by=order_by, sort_by=sort_by)
        except Exception as err:
            self.logger.error(err)
            self.exception = DatabaseException(MessagesEnum.LIST_ERROR)

        return total

    def find(self, request: dict):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))
        raise ServiceException(MessagesEnum.METHOD_NOT_IMPLEMENTED_ERROR)

    def get(self, request: dict, uuid):
        self.logger.info('method: {} - request: {}'
                         .format(get_function_name(), request))

        self.logger.info('method: {} - uuid: {}'
                         .format(get_function_name(), uuid))

        data = []
        where = request['where']

        try:
            fields = request['fields']
            value = uuid
            data = self.device_repository.get(
                value, key=self.device_repository.UUID_KEY, where=where, fields=fields
            )

            if self.DEBUG:
                self.logger.info('data: {}'.format(data))

            # convert to vo and prepare for api response
            if data:
                data = DeviceVO(data, default_values=False).to_api_response()

            # set exception if it happens
            if self.device_repository.get_exception():
                raise DatabaseException(MessagesEnum.FIND_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def create(self, request: dict):
        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            device_vo = DeviceVO(data)
            created = self.device_repository.create(device_vo)

            if created:
                # convert to vo and prepare for api response
                data = device_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def update(self, request: dict, uuid):

        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        original_device = self.device_repository.get(uuid, key=self.device_repository.UUID_KEY)
        if original_device is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_device)
 
        original_device.update(data)
        data = original_device

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            updated_at = helper.datetime_now_with_timezone()
            data['updated_at'] = updated_at
            device_vo = DeviceVO(data)

            updated = self.device_repository.update(device_vo, uuid, key=self.device_repository.UUID_KEY)

            if updated:
                # convert to vo and prepare for api response
                data = device_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def soft_update(self, request: dict, uuid):

        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))

        original_device = self.device_repository.get(uuid, key=self.device_repository.UUID_KEY)
        if original_device is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_device)
 
        device_copy = copy.deepcopy(original_device)
        device_copy.update(data)
        data = device_copy
 

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            updated_at = helper.datetime_now_with_timezone()
            data['updated_at'] = updated_at

            device_vo = DeviceVO(data)
            updated = self.device_repository.update(device_vo, uuid, key=self.device_repository.UUID_KEY)

            if updated:
                # convert to vo and prepare for api response
                data = device_vo.to_api_response()
            else:
                data = None
                # set exception if it happens
                raise DatabaseException(MessagesEnum.CREATE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return data

    def delete(self, request: dict, uuid):

        self.logger.info('method: {} - request: {}'.format(get_function_name(), request))
        result = False

        original_device = self.device_repository.get(uuid, key=self.device_repository.UUID_KEY)
        if original_device is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:

            updated = self.device_repository.soft_delete(value=uuid, key=self.device_repository.UUID_KEY)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return result

    def validate_data(self, data, original_device):
        allowed_fields = list(original_device.keys())
        try:
            allowed_fields.remove(self.device_repository.UUID_KEY)
            allowed_fields.remove(self.device_repository.PK)
            allowed_fields.remove('updated_at')
            allowed_fields.remove('created_at')
            allowed_fields.remove('deleted_at')
        except Exception as err:
            self.logger.error(err)
        fields = list(data.keys())
        for field in fields:
            if not field in allowed_fields:
                exception = ValidationException(MessagesEnum.VALIDATION_ERROR)
                exception.params = [filter_xss_injection(data[field]), filter_xss_injection(field)]
                exception.set_message_params()
                raise exception
