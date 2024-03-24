"""
HealthCheck Resources Module for Application
Version: 1.0.0
"""
import os
import requests
from boot import get_environment
from application.aws.sqs import SQS
from application.database.influxdb import InfluxDBConnector
from application.database.mysql import MySQLConnector
from application.database.redis import RedisConnector
from application.database.postgre import PostgreSQLConnector
from application.database.mysql_alchemy import AlchemyConnector
from application.services.v1.healthcheck import AbstractHealthCheck, HealthCheckResult 


class SelfConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, http_client=None):
        super().__init__(logger=logger, config=config)
        self.http_client = http_client if http_client is not None else requests

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)
        # para o ambiente docker implementar uma verificação compativel
        if get_environment() == "development":
            result = True
            #     # retry for docker
            #     url = "http://0.0.0.0:5000"
            #     url = url + "/docs"
            #     check_result, description, result = self.do_request(check_result, description, result, url)
            # else:
            #     description = "internal error"
            #     check_result = HealthCheckResult.degraded(description)
        else:
            try:
                result = True
                # todo migrar para usar self.config e adicionar API_PORT
                url = os.environ["API_SERVER"] if "API_SERVER" in os.environ else "http://0.0.0.0:5000"
                url = url + "/docs"
                try:
                    check_result, description, result = self.do_request(check_result, description, result, url)
                except Exception as err:
                    self.logger.error(err)
                    result = False

            except Exception as err:
                self.logger.error(err)
                description = "internal error"
                check_result = HealthCheckResult.degraded(description)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result

    def do_request(self, check_result, description, result, url):
        self.logger.info("requesting url: {}".format(url))
        response = self.http_client.get(url, timeout=2)
        if response:
            if response.status_code == 200:
                result = True
                description = "Connection successful"
            else:
                result = False
                description = "Something wrong"
                check_result = HealthCheckResult.degraded(description)
        else:
            raise Exception("Unable to connect")
        return check_result, description, result


class MysqlConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, mysql_connector=None):
        super().__init__(logger=logger, config=config)
        # database connection
        self.mysql_connector = mysql_connector if mysql_connector is not None else MySQLConnector()

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.mysql_connector:
                connection = self.mysql_connector.get_connection()
                connection.connect()
                connection.ping()
                result = True
                description = "Connection successful"
            else:
                raise Exception("mysql_connector is None")
        except Exception as err:
            self.logger.error(err)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result


class AlchemyMysqlConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, alchemy_connector=None):
        super().__init__(logger=logger, config=config)
        # database connection
        self.alchemy_connector = alchemy_connector if alchemy_connector is not None else AlchemyConnector()

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.alchemy_connector:
                result = self.alchemy_connector.get_status()  
                description = "Connection successful"
            else:
                raise Exception("AlchemyConnector is None")
        except Exception as err:
            self.logger.error(err)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result



class InfluxDBConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, influx_connector=None):
        super().__init__(logger=logger, config=config)
        # database connection
        self.influx_connector = influx_connector if influx_connector is not None else InfluxDBConnector()

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.influx_connector:
                result = self.influx_connector.get_status()  
                description = "Connection successful"
            else:
                raise Exception("InfluxDB is None")
        except Exception as err:
            self.logger.error(err)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result


class PostgreConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, postgre_connector=None):
        super().__init__(logger=logger, config=config)
        # database connection
        self.postgre_connector = postgre_connector if postgre_connector is not None else PostgreSQLConnector()

    def check_health(self):
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.postgre_connector:
                connection = self.postgre_connector.get_connection()
                connection.isexecuting() 
                description = "Connection successful"
            else:
                raise Exception("postgre_connector is None")
        except Exception as err:
            self.logger.error(err)

        if self.postgre_connector:
            check_result = HealthCheckResult.healthy(description)
        return check_result


class RedisConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, redis_connector=None):
        super().__init__(logger=logger, config=config)
        # database connection
        self.redis_connector = redis_connector if redis_connector is not None else RedisConnector()

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.redis_connector:
                redis_connection = self.redis_connector.get_connection()
                result = redis_connection.set('connection', 'true')
                description = "Connection successful"
            else:
                raise Exception("redis_connection is None")
        except Exception as err:
            self.logger.error(err)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result


class SQSConnectionHealthCheck(AbstractHealthCheck):
    def __init__(self, logger=None, config=None, sqs=None):
        super().__init__(logger=logger, config=config)
        # sqs connection
        self.sqs = sqs if sqs is not None else SQS()

    def check_health(self):
        result = False
        description = "Unable to connect"
        check_result = HealthCheckResult.unhealthy(description)

        try:
            if self.sqs:
                connection = self.sqs.connect()
                if connection:
                    result = True
                    description = "Connection successful"
            else:
                raise Exception("redis_connection is None")
        except Exception as err:
            self.logger.error(err)

        if result:
            check_result = HealthCheckResult.healthy(description)
        return check_result
