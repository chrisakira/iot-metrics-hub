"""
Mysql Data Repository Module for Application
Version: 1.0.0
"""
from datetime import datetime  
from application.config import get_config
from application.vos.data import DataVO
from application.repositories.v1.influxdb import AbstractRepository
from application.request_control import Order, Pagination, PaginationType
from application.enums.messages import MessagesEnum
from application.exceptions import DatabaseException, ValidationException, ServiceException
import random
import time

config = get_config()
class DataRepository(AbstractRepository):

    def __init__(self, logger=None, influxdb_connector=None):
        super().__init__(logger, influxdb_connector)

    def insert(self, data: DataVO, metadata: DataVO):
        self.logger.info(f"DB connector : {self.connection}")
        if "timestamp" not in data:
            self.logger.debug("Timestamp not found in data, adding current timestamp")
            data.timestamp = int(datetime.now().timestamp() * 1000)
        timestamp = data.timestamp
        del data.timestamp
        str_data =str(metadata.table) +"," + f'mac_address={metadata.mac_address} ' + ",".join([f"{key}={value}" for key, value in data.to_dict().items()]) + " " + str(timestamp)
        insert_data = [str_data]
 
        try: 
            if self.connection is None:
                self.logger.error("Connection not found")
                error = DatabaseException(MessagesEnum.DATABASE_CONNECTION_ERROR)
                error.params = 'Connection not found'
                self._exception = error
                raise self._exception
            self.connection.write_points(insert_data, time_precision='ms', batch_size=len(insert_data), protocol='line') 
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            raise self._exception 
        return True

    def insert_array(self, data_array, metadata: DataVO, precision = 'ms'):
        new_timestamp = int(datetime.now().timestamp() * 1000)
        insert_data = [] 
        for data in data_array:
            if "timestamp" not in data:
                data.timestamp = new_timestamp
            timestamp = int(data.timestamp)  
            del data.timestamp
            str_data =str(metadata.table) +"," + f'mac_address={metadata.mac_address} ' + ",".join([f"{key}={value}" for key, value in data.to_dict().items()]) + " " + str(timestamp)
            insert_data.append(str_data)
 
        try: 
            if self.connection is None:
                self.logger.error("Connection not found")
                error = DatabaseException(MessagesEnum.DATABASE_CONNECTION_ERROR)
                error.params = 'Connection not found'
                self._exception = error
                raise self._exception
            self.connection.write_points(insert_data, time_precision=precision, batch_size=len(insert_data), protocol='line') 
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            raise self._exception 
        return True

    def insert_mf4(self, data: DataVO, metadata: DataVO):
        self.logger.info(f"DB connector : {self.connection}")
        if "timestamp_CG_0" not in data:
            self.logger.debug("Timestamp not found in data, adding current timestamp")
            error = DatabaseException(MessagesEnum.VALIDATION_ERROR)
            error.params = 'Timestamp not found in data'
            self._exception = error
            raise self._exception
        timestamp = data.timestamp_CG_0 
        str_data =str(metadata.table) +"," + f'mac_address={metadata.mac_address} ' + ",".join([f"{key}={value}" for key, value in data.to_dict().items()]) + " " + str(timestamp)
        insert_data = [str_data]
 
        try: 
            if self.connection is None:
                self.logger.error("Connection not found")
                error = DatabaseException(MessagesEnum.DATABASE_CONNECTION_ERROR)
                error.params = 'Connection not found'
                self._exception = error
                raise self._exception
            self.connection.write_points(insert_data, time_precision='ms', batch_size=len(insert_data), protocol='line') 
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            raise self._exception 
        return True
 
    def insert_array_mf4(self, data_array, metadata: DataVO): 
        insert_data = []
        self.logger.info(f"Metadata : {metadata}")
        for data in data_array:
            if not any(key.startswith("timestamp_CG") for key in data):
                error = DatabaseException(MessagesEnum.VALIDATION_ERROR)
                error.params = 'Timestamp not found in data'
                self._exception = error
                raise self._exception
            timestamp = int(next(value for key, value in data.to_dict().items() if key.startswith("timestamp_CG")))
            str_data =str(metadata.table) +"," + f'mac_address={metadata.mac_address} ' + ",".join([f"{key}={value}" for key, value in data.to_dict().items()]) + " " + str(timestamp)
            insert_data.append(str_data)
 
        try: 
            if self.connection is None:
                self.logger.error("Connection not found")
                error = DatabaseException(MessagesEnum.DATABASE_CONNECTION_ERROR)
                error.params = 'Connection not found'
                self._exception = error
                raise self._exception
            self.connection.write_points(insert_data, time_precision='ms', batch_size=len(insert_data), protocol='line') 
        except Exception as err:
            self.logger.error(err)
            self._exception = err
            raise self._exception 
        return True
