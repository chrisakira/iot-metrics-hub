"""This is the main file of the lambda application

This module contains the handler method
"""
import base64
import os
import pymysql
import boot
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from application import APP_NAME, APP_VERSION, http_helper
from application import helper
from application.config import get_config
from application.database.postgre import get_uri as get_postgre_uri, run_compatible_with_sqlalchemy as run_mysql_compatible_with_sqlalchemy
from application.database.mysql import get_uri as get_mysql_uri, run_compatible_with_sqlalchemy as run_postrgre_compatible_with_sqlalchemy
from application.database.mysql_alchemy import get_uri as get_mysql_uri
from application.enums.messages import MessagesEnum
from application.exceptions import ApiException, ValidationException, CustomException
from application.core import Application
from application.helper import open_vendor_file, print_routes
from application.http_helper import CUSTOM_DEFAULT_HEADERS, set_hateos_links, set_hateos_meta, get_favicon_32x32_data, get_favicon_16x16_data
from application.http_resources.request import ApiRequest
from application.http_resources.response import ApiResponse
from application.logging import get_logger, set_debug_mode
from application.openapi import api_schemas
from application.openapi import spec, get_doc, generate_openapi_yml
from application.services.healthcheck_manager import HealthCheckManager
from application.services.product_manager import ProductManager
from application.services.data_manager import DataManager
from application.services.device_manager import DeviceManager
from application.migrations import models
from flask   import request
from io import BytesIO
from asammdf import MDF
import json 
import requests

# load directly by boot
ENV = boot.get_environment()

# config
CONFIG = get_config()
# debug
DEBUG = helper.debug_mode()

# keep in this order, the app generic stream handler will be removed
APP = Application(APP_NAME)

session = requests.Session()

# Logger
LOGGER = get_logger(force=True)
# override the APP logger
APP.logger = LOGGER
# override the log configs
if DEBUG:
    # override to the level desired
    set_debug_mode(LOGGER)

API_ROOT = os.environ['API_ROOT'] if 'API_ROOT' in os.environ else ''
API_ROOT_ENDPOINT = API_ROOT if API_ROOT != '' or API_ROOT is None else '/'

LOGGER.info("API_ROOT_ENDPOINT: {}".format(API_ROOT_ENDPOINT))

# *************
# Doc
# *************
@APP.route(API_ROOT_ENDPOINT)
def index():
    """
    API Root path

    :return: Returns the name and the current version of the project

    # pylint: disable=line-too-long

    :rtype: flask.Response
    """
    body = {"app": f'{APP_NAME}:{APP_VERSION}'}
    return http_helper.create_response(body=body, status_code=200)

@APP.route(API_ROOT + '/alive')
def alive():
    """
    Health check path

    :return Returns an intelligent healthcheck that describe what resource are working or not.

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#healthcheck

    # pylint: disable=line-too-long
    See https://docs.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/monitor-app-health

    :rtype: flask.Response

    ---

        get:
            summary: Service Health Method
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                424:
                    description: Failed dependency response
                    content:
                        application/json:
                            schema: HealthCheckSchema
                503:
                    description: Service unavailable response
                    content:
                        application/json:
                            schema: HealthCheckSchema
            """
    service = HealthCheckManager()
    return service.check() 

@APP.route(API_ROOT + '/favicon-32x32.png')
def favicon():
    """
    Favicon path

    :return Returns a favicon for the browser with size 32x32
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_32x32_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)

@APP.route(API_ROOT + '/favicon-16x16.png')
def favicon16():
    """
    Favicon path

    :return Returns a favicon for the browser with size 16x16
    :rtype: flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "image/png"
    data = get_favicon_16x16_data()

    if helper.is_running_on_lambda():
        data_b64 = {
            'headers': headers,
            'statusCode': 200,
            'body': data,
            'isBase64Encoded': True
        }
        data = helper.to_json(data_b64)
        headers = {"Content-Type": "application/json"}
    else:
        data = base64.b64decode(data)

    return http_helper.create_response(body=data, status_code=200, headers=headers)

@APP.route(API_ROOT + '/docs')
def docs():
    """
    Swagger OpenApi documentation

    :return Returns the Swagger UI interface for test operations

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#openapiswagger

    :rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/html"
    html_file = open_vendor_file('./public/swagger/index.html', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)

@APP.route(API_ROOT + '/openapi.yml')
def openapi():
    """
    Swagger OpenApi documentation route

    :return Returns the openapi.yml generated the API specification file

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#openapiswagger

    :rtype flask.Response
    """
    headers = CUSTOM_DEFAULT_HEADERS.copy()
    headers['Content-Type'] = "text/yaml"
    html_file = open_vendor_file('./public/swagger/openapi.yml', 'r')
    html = html_file.read()
    return http_helper.create_response(
        body=html, status_code=200, headers=headers)


# *************
# Device
# *************
@APP.route(API_ROOT + '/v1/device', methods=['GET'])
def get_device_v1():
    """
    Get device route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response

        ---
        get:
            summary: Get device 
            parameters:
            - name: name
              in: query
              description: "Name of the device (Necessary only name or mac_address)"
              required: true
              schema:
                type: string
                example: Akira 
            - name: mac_address
              in: query
              description: "Mac Address of the device (Necessary only name or mac_address)"
              required: true
              schema:
                type: string
                example: 02:42:ac:11:22:33
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: DeviceGetResponseSchema
                4xx:
                    description: Record not found in the DB
                    content:
                        application/json:
                            schema: DeviceGetFindErrorResponseSchema
                4xy:
                    description: Missing parameter in the request
                    content:
                        application/json:
                            schema: DeviceGetParamErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: InternalErrorResponseSchema
        """
    request = ApiRequest().parse_request(APP) 

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    LOGGER.info(f'request: {request}')
    try:
        data = manager.get_device(request.where) 
        status_code = 200
        response.set_data(data) 

        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device/list', methods=['GET'])
def list_device_v1():
    """
    List devices route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response

        ---
        get:
            summary: Get device 
            parameters:
            - name: name
              in: query
              description: "Name of the device (Necessary only name or mac_address)"
              required: true
              schema:
                type: string
                example: Akira 
            - name: mac_address
              in: query
              description: "Mac Address of the device (Necessary only name or mac_address)"
              required: true
              schema:
                type: string
                example: 02:42:ac:11:22:33
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: DeviceGetResponseSchema
                4xx:
                    description: Record not found in the DB
                    content:
                        application/json:
                            schema: DeviceGetFindErrorResponseSchema
                4xy:
                    description: Missing parameter in the request
                    content:
                        application/json:
                            schema: DeviceGetParamErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: InternalErrorResponseSchema
        """
    request = ApiRequest().parse_request(APP) 

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    LOGGER.info(f'request: {request}')
    try:
        data = manager.list_device(request.where) 
        status_code = 200
        response.set_data(data) 

        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as err:
        LOGGER.error(err)
        error = ApiException(MessagesEnum.LIST_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device', methods=['POST'])
def create_device_v1():
    """
    Device create route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        post:
            summary: Device Create
            requestBody:
                description: 'Device to be created'
                required: true
                content:
                    application/json:
                        schema: DeviceSchema
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: DeviceGetResponseSchema
                4xx:
                    description: Missing parameter in the request
                    content:
                        application/json:
                            schema: DeviceGetParamErrorResponseSchema
                4xy:
                    description: Who knows ?????????
                    content:
                        application/json:
                            schema: UnkownErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: InternalErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.create_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device', methods=['PUT'])
def update_device_v1():
    """
    Device update route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        put:
            summary: Update the Device info in the DB
            requestBody:
                description: 'Device to be created'
                required: true
                content:
                    application/json:
                        schema: DeviceUpdateSchema 
            responses:
                200:
                    description: Success response (Responds only with the sent fields)
                    content:
                        application/json:
                            schema: DeviceGetResponseSchema
                4xx:
                    description: Record not found in the DB
                    content:
                        application/json:
                            schema: DeviceGetFindErrorResponseSchema
                4xy:
                    description: Missing parameter in the request
                    content:
                        application/json:
                            schema: DeviceGetParamErrorResponseSchema
                4yy:
                    description: Who knows ?????????
                    content:
                        application/json:
                            schema: UnkownErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: InternalErrorResponseSchema
            """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.update_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.UPDATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device', methods=['DELETE'])
def delete_device_v1():
    """
    Product delete route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
            ---
            delete:
                summary: Soft Product Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Product Id"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: ProductSoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.delete_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device/list', methods=['GET'])
def get_device_list_v1():
    """
    List devices route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        get:
            summary: Product Get
            parameters:
            - in: path
              name: uuid
              description: "Product Id"
              required: true
              schema:
                type: string
                format: uuid
                example: 4bcad46b-6978-488f-8153-1c49f8a45244
            - name: fields
              in: query
              description: "Filter fields with comma"
              required: false
              schema:
                type: string
                example:
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: HateosProductGetResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductGetErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductGetErrorResponseSchema
    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.list_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device/ping', methods=['GET'])
def ping_device_v1():
    """
    Product delete route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
            ---
            delete:
                summary: Soft Product Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Product Id"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: ProductSoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.ping_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/device/log', methods=['POST'])
def log_device_v1():
    """
    Product delete route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
            ---
            delete:
                summary: Soft Product Delete
                parameters:
                - in: path
                  name: uuid
                  description: "Product Id"
                  required: true
                  schema:
                    type: string
                    format: uuid
                    example: 4bcad46b-6978-488f-8153-1c49f8a45244
                responses:
                    200:
                        description: Success response
                        content:
                            application/json:
                                schema: ProductSoftDeleteResponseSchema
                    4xx:
                        description: Error response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    5xx:
                        description: Service fail response
                        content:
                            application/json:
                                schema: ProductSoftDeleteErrorResponseSchema
                    """
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(ApiRequest(request))
    response.set_hateos(True)

    manager = DeviceManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:
        data = manager.log_device(request.where)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)


# *************
# Data
# *************
@APP.route(API_ROOT + '/v1/data', methods=['POST'])
def insert_data_v1():
    """
    Insert data row in the table

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        post:
            summary: Product Create
            requestBody:
                description: 'Product to be created'
                required: true
                content:
                    application/json:
                        schema: ProductCreateRequestSchema
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: ProductCreateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
            """   
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request) 
    response.set_hateos(True)
    if 'where' not in request:
        LOGGER.error("Data or file field missing")
        error = ApiException(MessagesEnum.VALIDATION_ERROR)
        status_code = 400 
        response.set_exception(error) 
        return response.get_response(status_code)
    auth_token = str(request['where']['auth_token'])
    tokens = str(os.getenv('auth_token'))
    if(len(auth_token) > 5 and auth_token in tokens):
        del request['where']['auth_token']
        manager = DataManager(logger=LOGGER)
        manager.debug(DEBUG)
        try:
            data = manager.insert_data(request['where'])
            response.set_data(data)
            response.links = None
        except Exception as err:
            LOGGER.error(err)
            error = ApiException(MessagesEnum.LIST_ERROR)
            status_code = 400
            if manager.exception:
                error = manager.exception
            response.set_exception(error)

    else:
        LOGGER.error("Auth token failed")
        error = ApiException(MessagesEnum.VALIDATION_ERROR)
        error.params = str(request['where']['auth_token']),"auth_token"
        error.set_message_params()
        status_code = 400 
        response.set_exception(error) 
    return response.get_response(status_code)

    # return http_helper.create_response(body=body, status_code=200)

@APP.route(API_ROOT + '/v1/data/array', methods=['POST'])
def insert_array_v1():
    """
    Product create route

    :return Endpoint with RESTful pattern

    # pylint: disable=line-too-long
    See https://github.com/andersoncontreira/projects-guidelines#restful-e-hateos

    :rtype flask.Response
        ---
        post:
            summary: Product Create
            requestBody:
                description: 'Product to be created'
                required: true
                content:
                    application/json:
                        schema: ProductCreateRequestSchema
            responses:
                200:
                    description: Success response
                    content:
                        application/json:
                            schema: ProductCreateResponseSchema
                4xx:
                    description: Error response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
                5xx:
                    description: Service fail response
                    content:
                        application/json:
                            schema: ProductCreateErrorResponseSchema
            """   
    request = ApiRequest().parse_request(APP)
    LOGGER.info(f'request: {request}')

    status_code = 200
    response = ApiResponse(request) 
    response.set_hateos(True)
    auth_token = str(request['where']['auth_token'])
    tokens = str(os.getenv('auths'))
    if(len(auth_token) == 27 and auth_token in tokens):
        manager = BaseManager(logger=LOGGER, base_service=BaseService(logger=LOGGER))
        
        manager.debug(DEBUG)
        try:
            data = manager.process_array(request['where'])
            response.set_data(data)
            response.links = None
        except Exception as err:
            LOGGER.error(err)
            error = ApiException(MessagesEnum.LIST_ERROR)
            status_code = 400
            if manager.exception:
                error = manager.exception
            response.set_exception(error)

    else:
        LOGGER.error("Auth token failed")
        error = ApiException(MessagesEnum.VALIDATION_ERROR)
        error.params = str(request['where']['auth_token']),"auth_token"
        error.set_message_params()
        status_code = 400 
        response.set_exception(error) 
    return response.get_response(status_code)

    # return http_helper.create_response(body=body, status_code=200)
 
@APP.route(API_ROOT + '/v1/data/mf4', methods=['POST'])
def insert_mf4_file():
    """
    API endpoint for inserting data and file.
    :return: Returns a JSON response with the status code and any error messages.
    :rtype: str
    """      
    status_code = 200
    response = ApiResponse() 
    response.set_hateos(True)
    if 'data' in request.form and 'file' in request.files:
        data = request.form['data']
        data = json.loads(data)
    else:
        LOGGER.error("Data or file field missing")
        error = ApiException(MessagesEnum.VALIDATION_ERROR)
        error.params = "Potato", "potato"
        error.set_message_params()
        status_code = 400 
        response.set_exception(error) 
        return response.get_response(status_code)
    auth_token = str(data['auth_token']) 
    tokens = str(os.getenv('auths'))
    if(len(auth_token) == 27 and auth_token in tokens):
        manager = DataManager(logger=LOGGER) 
        manager.debug(DEBUG)
        try:  
            manager.process_MF4(request.files['file'], data)
        except Exception as err:
            LOGGER.error(err)
            error = ApiException(MessagesEnum.LIST_ERROR)
            status_code = 400
            if manager.exception:
                error = manager.exception
            response.set_exception(error)

    else:
        LOGGER.error("Auth token failed")
        error = ApiException(MessagesEnum.VALIDATION_ERROR)
        error.params = str(data['auth_token']),"auth_token"
        error.set_message_params()
        status_code = 400 
        response.set_exception(error) 
    return response.get_response(status_code)

@APP.route(API_ROOT + '/v1/data/akira', methods=['POST'])
def insert_aki_file():     

    status_code = 200
    response = ApiResponse()
    response.set_hateos(True)
 
    manager = DataManager(logger=LOGGER)
    manager.debug(DEBUG)
    try:  
        data = manager.receive_file(request.get_data(),request.headers)  
        status_code = 200
        response.set_data(data)  
        # hateos
        response.links = None
        set_hateos_meta(request, response) 
    except CustomException as error:
        LOGGER.error(error)
        if not isinstance(error, ValidationException):
            error = ApiException(MessagesEnum.CREATE_ERROR)
        status_code = 400
        if manager.exception:
            error = manager.exception
        response.set_exception(error)

    return response.get_response(status_code)
    
    body = {"app": f'{APP_NAME}:{APP_VERSION}'}
    return http_helper.create_response(body=body, status_code=200)
 
# *************
# Doc
# *************
spec.path(view=alive, path=API_ROOT + "/alive", operations=get_doc(alive)) 
# *************
# Device
# *************
spec.path(view=get_device_v1, path="/v1/device", operations=get_doc(get_device_v1)) 
spec.path(view=create_device_v1, path="/v1/device", operations=get_doc(create_device_v1)) 
spec.path(view=update_device_v1, path="/v1/device", operations=get_doc(update_device_v1)) 
spec.path(view=delete_device_v1, path="/v1/device", operations=get_doc(delete_device_v1)) 
spec.path(view=get_device_list_v1, path="/v1/device/list", operations=get_doc(get_device_list_v1))
spec.path(view=ping_device_v1, path="/v1/device/ping", operations=get_doc(ping_device_v1))
spec.path(view=log_device_v1, path="/v1/device/log", operations=get_doc(log_device_v1))

# *************
# Data
# *************
spec.path(view=insert_data_v1, path="/v1/data", operations=get_doc(insert_data_v1)) 
spec.path(view=insert_array_v1, path="/v1/data/array", operations=get_doc(insert_array_v1))
spec.path(view=insert_mf4_file, path="/v1/data/mf4", operations=get_doc(insert_mf4_file))
spec.path(view=insert_aki_file, path="/v1/data/aki", operations=get_doc(insert_aki_file))

print_routes(APP)
print(f'Running at {ENV}')

# generate de openapi.yml
generate_openapi_yml(spec, LOGGER, force=True)

api_schemas.register()

# *************
# Migrations
# *************
# compatibility with sqlalchemy
# run_postrgre_compatible_with_sqlalchemy() # To use Postgre

run_mysql_compatible_with_sqlalchemy()
MySQL_URI = get_mysql_uri(CONFIG)
Postgre_URI = get_postgre_uri(CONFIG)

APP.config['SQLALCHEMY_DATABASE_URI'] = MySQL_URI
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

APP.logger.info('MySQL URI: {}'.format(MySQL_URI))
APP.logger.info('Postgre URI: {}'.format(Postgre_URI))
 
DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)

# Models
models.create(DB)
