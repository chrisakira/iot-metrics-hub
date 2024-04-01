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
import ast

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
            
            float_bytes = file.read(8)
            if b'#EOF' in float_bytes:
                break 
            if len(float_bytes) < 8:
                break
            float_value = struct.unpack('d', float_bytes)[0] 

            
            int_value = file.read(4)
            if b'#EOF' in int_value:
                break 
            int_value = struct.unpack('i', int_value)[0] 
        except Exception as e:
            return data
        data.append({str(int_value):float_value,"timestamp":int_value_, "measurement":int_value})    
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
        metadata = DataVO(request["meta_data"])
        data = DataVO(request["data"])  
        self.logger.info('metadata: {}'.format(metadata))
        self.logger.info('data: {}'.format(data))
        self.influxdb_data_repository.insert(data, metadata)
        if self.influxdb_data_repository._exception:
            self.exception = self.influxdb_data_repository._exception
            raise self.exception
        
        return True     
    
    def insert_array(self, request):  
        metadata = DataVO(request["meta_data"])
        data = DataVO(request["data"])   

        tmp_array = []

        for key, value in data.to_dict().items():
            values_list = ast.literal_eval(value)  # Convertendo a string JSON para lista
            for i, single_value in enumerate(values_list):
                if len(tmp_array) <= i:  # Se ainda não existe um dicionário para este índice
                    tmp_array.append({})  # Criar um novo dicionário
                tmp_array[i][key] = single_value   
        if len(tmp_array) == 0:
            error = ValidationException(MessagesEnum.REQUEST_ERROR)
            error.params = 'Data not found'
            self.exception = error
            raise self.exception
        data_array = []
        for tmp in tmp_array:
            data_array.append(DataVO(tmp)) 
        if len(tmp_array) == 1:
            self.influxdb_data_repository.insert(data, metadata)
        else:
            self.influxdb_data_repository.insert_array(data_array, metadata)
        
        if self.influxdb_data_repository._exception:
            self.exception = self.influxdb_data_repository._exception
            raise self.exception
        
        return True
    
       
    def receive_file(self, file, headers): 
        if file == b'':
            raise ValidationException(MessagesEnum.REQUEST_ERROR)
        
        mac_value = headers['Cookie'].split("=")[1]
        device = headers['Cookie'].split("=")[0]
        metadata = DataVO()
        metadata.mac_address=mac_value
        metadata.table="Banana"
        parsed_bin_data = read_binary_file(file)  
        self.logger.info('parsed_bin_data size: {}'.format(len(parsed_bin_data)))        
        data = []
        for bin in parsed_bin_data:
            if bin["measurement"] == 3 or bin["measurement"] == 4:
                self.logger.info('bin: {}'.format(bin))
            data_ = DataVO(bin) 
            data.append(data_)
        self.influxdb_data_repository.insert_array(data, metadata, 'u')
        if self.influxdb_data_repository._exception:
            self.exception = self.influxdb_data_repository._exception
            raise self.exception
        
        return True


    def process_MF4(self, file, request): 
        file = BytesIO(file.read())
        mdf = MDF(file)        
        data = DataVO().MF4_Loader_Data(mdf) 
        metadata = DataVO(request) 
        tmp_array = [] 

        for key, value in data.to_dict().items():
            values_list = (value)  # Convertendo a string JSON para lista
            for i, single_value in enumerate(values_list):
                if len(tmp_array) <= i:  # Se ainda não existe um dicionário para este índice
                    tmp_array.append({})  # Criar um novo dicionário
                tmp_array[i][key] = single_value
        
        if len(tmp_array) == 0:
            error = ValidationException(MessagesEnum.REQUEST_ERROR)
            error.params = 'Data not found'
            self.exception = error
            raise self.exception
        
        data_array = []
        for tmp in tmp_array:
            data_array.append(DataVO(tmp)) 
             
        if len(tmp_array) == 1:
            self.influxdb_data_repository.insert_mf4(data, metadata)
        else:
            self.influxdb_data_repository.insert_array_mf4(data_array, metadata)
         
        
        data_array = []  
        return True
        
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
