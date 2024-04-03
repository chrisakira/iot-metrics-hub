"""
App Messages Enum Module for Application
Version: 1.0.0
"""
from enum import IntEnum


class MessagesEnum(IntEnum):

    def __new__(cls, value, label, message='', status_code = 400):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.code = value
        obj.label = label
        obj.message = message
        obj.status_code = status_code
        return obj

    # Common messages 1-10
    OK = 1, 'common.success', 'Success', 200
    NOK = 2, 'common.error.nok', '%s', 400

    REQUEST_ERROR = 3, 'common.error.request_error', '%s', 400
    UNSUPPORTED_MEDIA_TYPE_ERROR = 4, 'common.error.unsupported_media_type_error', \
        'Unsupported media type: %s, supported types are (%s)' , 400
    METHOD_NOT_IMPLEMENTED_ERROR = 5, 'common.error.method_not_implemented_error', 'Method not implemented yet', 501
    UNKNOWN_ERROR = 6, 'common.error.unknown_error', 'Unknown error', 400
    INTERNAL_SERVER_ERROR = 7, 'common.error.internal_server_error', 'Internal Server Error', 500
    INVALID_KEY_ERROR =8, 'common.error.invalid_key_error', 'Invalid key in database query: %s', 400
    # Request errors 11 - 30
    LIST_ERROR = 11, 'common.error.list_error', 'Unable to return the list data, please review your request', 400
    FILTERS_ERROR = 12, 'common.error.filters_error', 'Filters must be informed', 400
    PARAM_REQUIRED_ERROR = 13, 'common.error.param_required_error', 'Parameter %s is required', 400
    FIND_ERROR = 14, 'common.error.find_error', 'Unable to find the record %s', 400
    INVALID_FILTER_ERROR = 15, 'common.error.invalid_filter_error', 'Invalid filter in request', 400
    INVALID_FIELD_FILTER_ERROR = 16, 'common.error.invalid_filter_error', \
        'Invalid filter value (%s) for filter (%s). Expected (%s)', 400

    CREATE_ERROR = 17, 'common.error.create_error', 'Unable to create the record', 400
    UPDATE_ERROR = 18, 'common.error.update_error', 'Unable to update the record', 400
    DELETE_ERROR = 18, 'common.error.delete_error', 'Unable to delete the record', 400
    SOFT_DELETE_ERROR = 18, 'common.error.soft_delete_error', 'Unable to disable the record', 400

    # validation 31 - 50
    VALIDATION_ERROR = 31, 'common.error.validation_error', 'Validation error, please review your params: value (%s) for param (%s)', 400
    INVALID_ISO_DATE_ERROR = 32, 'common.error.invalid_iso_date', 'Invalid iso date value (%s) for param (%s)', 400

    # Database errors 51 - 100
    QUERY_ERROR = 51, 'common.error.query_error', 'Unable to execute the query', 400
    INVALID_ENTITY_ID = 52, 'common.error.invalid_entity_id', 'Unable to find the entity', 400
    ENTITY_DELETION_SUCCESS = 53, 'common.entity_deletion_success', 'Entity deleted with success', 400

    # Events 101 - 200
    EVENT_NOT_REGISTERED_ERROR = 101, 'common.error.event_not_registered_error', 'Event not registered', 400
    EVENT_REGISTERED_WITH_SUCCESS = 102, 'common.event_registered_with_success', 'Event registered with success', 400
    EVENT_NOT_SENT_ERROR = 103, 'common.error.event_not_sent_error', 'Event not sent', 400
    EVENT_ALREADY_REGISTERED_ERROR = 104, 'common.error.event_already_registered_error', 'Event already registered', 400
    EVENT_TYPE_UNKNOWN_ERROR = 105, 'common.error.event_type_unknown_error', 'Event type unknown: (%s)', 400

    # DataBase Exceptions 201 - 300
    DATABASE_CONNECTION_ERROR = 201, 'common.error.data_base_not_connected', 'Unable to reach the database', 400
    UNMAPPING_ERROR = 202, 'common.error.unmapping_error', 'Unable to unmapping the data', 400
