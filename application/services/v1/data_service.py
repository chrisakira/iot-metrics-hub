"""
Data Service for Application
Version: 1.0.0
"""
import copy

from datetime import datetime
from application import helper
from application.database.mysql_alchemy import AlchemyConnector
from application.database.mysql import MySQLConnector
from application.database.influxdb import InfluxDBConnector
from application.database.redis import RedisConnector
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException, ServiceException
from application.filter_helper import filter_xss_injection
from application.helper import get_function_name
from application.logging import get_logger
from application.repositories.v1.alchemy.data_repository import DataRepository as AlchemyDataRepository
from application.repositories.v1.influxdb.data_repository import DataRepository as InfluxDBDataRepository
from application.repositories.v1.mysql.data_repository import DataRepository as MysqlDataRepository
from application.repositories.v1.redis.data_repository import DataRepository as RedisDataRepository
from application.vos.data import DataVO
from io import BytesIO
from asammdf import MDF
import pytz
import struct
import io

def read_binary_file(file):
    data = []
    file = io.BytesIO(file)
    while True:
        try:
            int_bytes = file.read(8)
            if b'#EOF' in int_bytes:
                break 
            if len(int_bytes) < 8:
                break
            int_value = struct.unpack('q', int_bytes)[0]
            int_value_ = int_value 
            
            float_bytes = file.read(4)
            if b'#EOF' in float_bytes:
                break 
            if len(float_bytes) < 4:
                break
            float_value = struct.unpack('f', float_bytes)[0] 

            
            int_value = file.read(4)
            if b'#EOF' in int_value:
                break 
            int_value = struct.unpack('i', int_value)[0] 
        except Exception as e:
            return data
        data.append((float_value, int_value_, int_value))
        

    return data
class DataService:
    DEBUG = False
    REDIS_ENABLED = False

    def __init__(self, logger=None, mysql_connector=None, influxdb_connector=None, alchemy_session=None, redis_connector=None, data_repository=None,
                redis_data_repository=None, alchemy_data_repository=None, influxdb_data_repository=None):
        # logger
        self.logger = logger if logger is None else get_logger()
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()
        
        self.alchemy_session = alchemy_session if alchemy_session is not None else AlchemyConnector()
        
        self.influxdb_connector = influxdb_connector if influxdb_connector is not None else InfluxDBConnector()
        # todo passar apenas connector
        # mysql repository
        self.data_repository = data_repository if data_repository is not None \
            else MysqlDataRepository(mysql_connection=self.mysql_connector.get_connection())
        
        self.alchemy_data_repository = alchemy_data_repository if alchemy_data_repository is not None \
            else AlchemyDataRepository(alchemy_session=self.alchemy_session.get_session(self.alchemy_session.get_engine()))

        self.influxdb_data_repository = influxdb_data_repository if influxdb_data_repository is not None \
            else InfluxDBDataRepository(influxdb_connector=self.influxdb_connector.get_connection())

        # exception
        self.exception = None

        if self.REDIS_ENABLED:
            # redis connection
            self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()
            # todo passar apenas connector
            # redis repository
            self.redis_data_repository = redis_data_repository if redis_data_repository is not None \
                else RedisDataRepository(redis_connection=self.redis_connector.get_connection())

        self.debug(self.DEBUG)

    def debug(self, flag: bool = False):
        self.DEBUG = flag
        self.data_repository.debug = self.DEBUG
        if self.REDIS_ENABLED:
            self.redis_data_repository.debug = self.DEBUG
            
    def insert_data(self, request): 
        self.logger.info('request: {}', request)
        # self.influxdb_data_repository.insert()
        
        return True
    
    def test(self): 
        self.influxdb_data_repository.insert()
        
        return True
    
       
    def receive_file(self, file, headers):  
        if file == b'':
            raise ValidationException(MessagesEnum.REQUEST_ERROR)
        data = DataVO()
        if(len(file) < 8):
            return True
        self.logger.info('file: {}'.format(len(file)))
        parsed_bin_data = read_binary_file(file)
        parsed_bin_data_count = len(parsed_bin_data) 
        
        self.logger.info('parsed_bin_data_count: {}'.format(parsed_bin_data_count))
        for bin_data in parsed_bin_data: 
            self.logger.info('bin_data: {}'.format(bin_data))
            # data.mac_address = "00:00:01:02:FF:FF"
            # data.value = bin_data[0]
            # data.timestamp = bin_data[1]
            # data.measurement = bin_data[2]
            # self.alchemy_data_repository.create(data) 
        return True


    def process_MF4(self, file, headers):
        file = BytesIO(file.read())
        mdf = MDF(file)      
        result = self.alchemy_data_repository.check_table(headers)
        if (result): 
            base_vo = DataVO().MF4_Loader_Data(mdf) 
            data = self.base_service.create_array(headers, base_vo)
            if (data):
                return 200
            else:
                raise 424
        else: 
            base_vo_ = DataVO().MF4_Loader_Types(mdf) 
            result_ = self.base_service.create_table(headers, base_vo_)
            if (result_): 
                base_vo = DataVO().MF4_Loader_Data(mdf) 
                data = self.base_service.create_array(headers, base_vo)
                if (data):
                    return 200
                else:
                    raise 424
            else:
                raise 424
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
            data = self.data_repository.list(
                where=where, offset=offset, limit=limit, order_by=order_by,
                sort_by=sort_by, fields=fields)

            # convert to vo and prepare for api response
            if data:
                vo_data = []
                for item in data:
                    vo_data.append(DataVO(item, default_values=False).to_api_response())
                data = vo_data

            # set exception if it happens
            if self.data_repository.get_exception():
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
            total = self.data_repository.count(
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
            data = self.data_repository.get(
                value, key=self.data_repository.UUID_KEY, where=where, fields=fields
            )

            if self.DEBUG:
                self.logger.info('data: {}'.format(data))

            # convert to vo and prepare for api response
            if data:
                data = DataVO(data, default_values=False).to_api_response()

            # set exception if it happens
            if self.data_repository.get_exception():
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

            data_vo = DataVO(data)
            created = self.data_repository.create(data_vo)

            if created:
                # convert to vo and prepare for api response
                data = data_vo.to_api_response()
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

        original_data = self.data_repository.get(uuid, key=self.data_repository.UUID_KEY)
        if original_data is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_data)
 
        original_data.update(data)
        data = original_data

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            updated_at = helper.datetime_now_with_timezone()
            data['updated_at'] = updated_at
            data_vo = DataVO(data)

            updated = self.data_repository.update(data_vo, uuid, key=self.data_repository.UUID_KEY)

            if updated:
                # convert to vo and prepare for api response
                data = data_vo.to_api_response()
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

        original_data = self.data_repository.get(uuid, key=self.data_repository.UUID_KEY)
        if original_data is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        data = request['where']
        if self.DEBUG:
            self.logger.info('method: {} - data: {}'.format(get_function_name(), data))

        # validate the request payload
        self.validate_data(data, original_data)
 
        data_copy = copy.deepcopy(original_data)
        data_copy.update(data)
        data = data_copy
 

        try:

            if data == dict():
                raise ValidationException(MessagesEnum.REQUEST_ERROR)

            updated_at = helper.datetime_now_with_timezone()
            data['updated_at'] = updated_at

            data_vo = DataVO(data)
            updated = self.data_repository.update(data_vo, uuid, key=self.data_repository.UUID_KEY)

            if updated:
                # convert to vo and prepare for api response
                data = data_vo.to_api_response()
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

        original_data = self.data_repository.get(uuid, key=self.data_repository.UUID_KEY)
        if original_data is None:
            raise DatabaseException(MessagesEnum.FIND_ERROR)

        try:

            updated = self.data_repository.soft_delete(value=uuid, key=self.data_repository.UUID_KEY)

            if updated:
                result = True
            else:
                # set exception if it happens
                raise DatabaseException(MessagesEnum.SOFT_DELETE_ERROR)

        except Exception as err:
            self.logger.error(err)
            self.exception = err

        return result

    def validate_data(self, data, original_data):
        allowed_fields = list(original_data.keys())
        try:
            allowed_fields.remove(self.data_repository.UUID_KEY)
            allowed_fields.remove(self.data_repository.PK)
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
