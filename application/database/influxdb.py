"""
InfluxDB Module for Application
Version: 1.0.0
"""
from time import sleep

from influxdb import InfluxDBClient

from application.config import get_config, Configuration
from application.logging import get_logger

_CONNECTION = False
_RETRY_COUNT = 0
_MAX_RETRY_ATTEMPTS = 3


def reset():
    global _CONNECTION
    _CONNECTION = False


def get_uri(config: Configuration = None):
    if config is None:
        config = get_config()
    DB_HOST = 'localhost'
    if config.get('RUNNING_IN_CONTAINER'):
        DB_HOST = config.get('INFLUXDB_HOST')
    uri = 'http://{}:{}/{}'.format(
        DB_HOST,
        config.get('INFLUXDB_PORT'),
        config.get('INFLUXDB_DATABASE'))

    return uri


class InfluxDBConnector:
    def __init__(self, config=None, logger=None):
        # logger
        self.logger = logger if logger is not None else get_logger()
        # logger
        self.config = config if config is not None else get_config()
        # last_exception
        self.exception = None

    def get_connection(self, connect=True, retry=False):
        global _CONNECTION, _RETRY_COUNT, _MAX_RETRY_ATTEMPTS
        if not _CONNECTION:
            connection = None

            try:
                params = {
                    'host': self.config.get('INFLUX_DB_HOST'),
                    'port': self.config.get('INFLUX_DB_PORT'),
                    'username': self.config.get('DB_USER'),
                    'password': self.config.get('DB_PASSWORD'),
                    'database': self.config.get('DB')
                }

                connection = InfluxDBClient(host=params['host'],
                                            port=params['port'],
                                            username=params['username'],
                                            password=params['password'],
                                            database=params['database'])
                if connect:
                    connection.ping()
                _CONNECTION = connection
                _RETRY_COUNT = 0
                self.logger.info('Connected')
            except Exception as err:
                if _RETRY_COUNT == _MAX_RETRY_ATTEMPTS:
                    _RETRY_COUNT = 0
                    self.logger.error(err)
                    connection = None
                    return connection
                else:
                    self.logger.error(err)
                    self.logger.info('Trying to reconnect... {}'.format(_RETRY_COUNT))

                    sleep(0.1)
                    # retry
                    if not retry:
                        _RETRY_COUNT += 1
                        # Fix para tratar diff entre docker/local
                        if self.config.get('INFLUXDB_HOST') == 'influxdb':
                            old_value = self.config.get('INFLUXDB_HOST')
                            self.config.set('INFLUXDB_HOST', '127.0.0.1')
                            self.logger.info(
                                'Changing the endpoint from {} to {}'.format(old_value, self.config.get('INFLUXDB_HOST')))
                        return self.get_connection(True)
        else:
            connection = _CONNECTION

        return connection
