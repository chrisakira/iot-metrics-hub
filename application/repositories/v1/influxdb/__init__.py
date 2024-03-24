"""
InfluxDB Repositories Module for Application
Version: 1.0.0
"""
from application.database.influxdb import InfluxDBConnector
from application.logging import get_logger


class AbstractRepository:
    _MAX_ATTEMPTS = 5
    def __init__(self, logger, influxdb_connection):
        self.logger = logger if logger is not None else get_logger()
        self.connection = influxdb_connection if influxdb_connection is not None else InfluxDBConnector().get_connection()
        self._exception = None
        self.debug = False

    def get_connection(self):
        return self.connection

    def get_exception(self):
        return self._exception

    def _close(self):
        self.connection.close()
