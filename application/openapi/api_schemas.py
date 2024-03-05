"""
API Schemas Module for Application
Version: 1.0.0
"""
from marshmallow import Schema, fields, validate

from application.enums.messages import MessagesEnum
from application.openapi.schemas import DeletionSchema, RequestControlSchema, MetaSchema, LinkSchema, ErrorSchema, \
    HateosDefaultListResponseSchema, DefaultResponseSchema, HateosDefaultResponseSchema


# ***************************
# Device
# *************************** 
class DeviceSchema(Schema): 
    name =          fields.Str(         description="Name of the device",                               example="Akira",                required=True)
    mac_address =   fields.Str(         description="Mac Address of the device",                        example="02:42:ac:11:22:33",    required=True)
    description =   fields.Str(         description="Description of the device",                        example="Device description",   required=True)
    active =        fields.Int(         description="Defines if the device is active",                  exemple="1", validate=validate.OneOf([0, 1]),           required=True)
    status =        fields.Int(         description="Defines the status of the device",                 exemple="1", validate=validate.OneOf([0, 1, 2, 3, 4]),  required=True)
    model =         fields.Str(         description="Model of the device",                              example="ESP32",    required=True)
    firmware =      fields.Str(         description="Firmware running in the device",                   example="V0.0.1",   required=True)
    last_seen =     fields.DateTime(    description="last time the device was seen",                    example="2024-02-29 03:21:13.000")
    created_at =    fields.DateTime(    description="Creation date of the device in the DB",            example="2024-02-29 03:21:13.000")
    updated_at =    fields.DateTime(    description="Last time the device was updated",                 example="2024-02-29 03:21:13.000")
    deleted_at =    fields.DateTime(    description="When the device was deleted",                      example="2024-02-29 03:21:13.000")
    delete_status = fields.Int(         description="Defines if the device was marked for deletion",    exemple="0", validate=validate.OneOf([0, 1]))
    
class DeviceUpdateSchema(Schema): 
    name =          fields.Str(         description="Name of the device",                               example="Akira",                required=True)
    mac_address =   fields.Str(         description="Mac Address of the device",                        example="02:42:ac:11:22:33",    required=True)
    description =   fields.Str(         description="Description of the device",                        example="Device description")
    active =        fields.Int(         description="Defines if the device is active",                  exemple="1", validate=validate.OneOf([0, 1]))
    status =        fields.Int(         description="Defines the status of the device",                 exemple="1", validate=validate.OneOf([0, 1, 2, 3, 4]))
    model =         fields.Str(         description="Model of the device",                              example="ESP32")
    firmware =      fields.Str(         description="Firmware running in the device",                   example="V0.0.1")
    last_seen =     fields.DateTime(    description="last time the device was seen",                    example="2024-02-29 03:21:13.000")
    created_at =    fields.DateTime(    description="Creation date of the device in the DB",            example="2024-02-29 03:21:13.000")
    updated_at =    fields.DateTime(    description="Last time the device was updated",                 example="2024-02-29 03:21:13.000")
    deleted_at =    fields.DateTime(    description="When the device was deleted",                      example="2024-02-29 03:21:13.000")
    delete_status = fields.Int(         description="Defines if the device was marked for deletion",    exemple="0", validate=validate.OneOf([0, 1]))

class DeviceLogSchema(Schema):
    name =          fields.Str(description="Name of the device to be logged (It must contain the name of the device or the mac)",        example="Akira",               required=True)
    mac_address =   fields.Str(description="Mac address of the device to be logged (It must contain the name of the device or the mac)", example="02:42:ac:11:22:33",   required=True)
    type =          fields.Str(description="Type of the message",           example="INFO, ERROR, DEBUG",   required=True)
    message =       fields.Str(description="Message to be logged",          example="Here lies my message", required=True)
    timestamp =     fields.DateTime(description="Timestamp of the message", example="2024-02-29 03:21:13.000")

class DeviceGetResponseSchema(DefaultResponseSchema):
    data = fields.Nested(DeviceSchema)
    
class DeviceGetFindErrorResponseSchema(ErrorSchema):
    code =      fields.Int(example=MessagesEnum.FIND_ERROR.code)
    label =     fields.Str(example=MessagesEnum.FIND_ERROR.label)
    message =   fields.Str(example=MessagesEnum.FIND_ERROR.message)
    
class DeviceGetParamErrorResponseSchema(ErrorSchema):
    code =      fields.Int(example=MessagesEnum.PARAM_REQUIRED_ERROR.code)
    label =     fields.Str(example=MessagesEnum.PARAM_REQUIRED_ERROR.label)
    message =   fields.Str(example=MessagesEnum.PARAM_REQUIRED_ERROR.message)
    
class UnkownErrorResponseSchema(ErrorSchema):
    code =      fields.Int(example=MessagesEnum.UNKNOWN_ERROR.code)
    label =     fields.Str(example=MessagesEnum.UNKNOWN_ERROR.label)
    message =   fields.Str(example=MessagesEnum.UNKNOWN_ERROR.message)

class InternalErrorResponseSchema(ErrorSchema):
    code =      fields.Int(example=MessagesEnum.INTERNAL_SERVER_ERROR.code)
    label =     fields.Str(example=MessagesEnum.INTERNAL_SERVER_ERROR.label)
    message =   fields.Str(example=MessagesEnum.INTERNAL_SERVER_ERROR.message)


# ***************************
# Product
# ***************************
class ProductSchema(Schema):
    id = fields.Int(example=1)
    sku = fields.Int(example=1)
    name = fields.Str(example="Common Pencil")
    description = fields.Str(example="Common Pencil Description")
    supplier_id = fields.Int(example=1)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    deleted_at = fields.DateTime()
    active = fields.Int(validate=validate.OneOf([0, 1]))
    uuid = fields.UUID(example="4bcad46b-6978-488f-8153-1c49f8a45244")


class HateosProductListResponseSchema(HateosDefaultListResponseSchema):
    data = fields.List(fields.Nested(ProductSchema))
    control = fields.Nested(RequestControlSchema)


class ProductListResponseSchema(DefaultResponseSchema):
    data = fields.List(fields.Nested(ProductSchema))
    control = fields.Nested(RequestControlSchema)


class ProductListErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.LIST_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.LIST_ERROR.label)
    message = fields.Str(example=MessagesEnum.LIST_ERROR.message)


class ProductGetResponseSchema(DefaultResponseSchema):
    data = fields.Nested(ProductSchema)


class HateosProductGetResponseSchema(HateosDefaultResponseSchema):
    data = fields.Nested(ProductSchema)


class ProductGetErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.FIND_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.FIND_ERROR.label)
    message = fields.Str(example=MessagesEnum.FIND_ERROR.message)


class ProductCreateRequestSchema(Schema):
    sku = fields.Int(example=1)
    name = fields.Str(example="Common Pencil")
    description = fields.Str(example="Common Pencil description")
    supplier_id = fields.Int(example=1)
    active = fields.Int(validate=validate.OneOf([0, 1]))


class ProductCreateResponseSchema(DefaultResponseSchema):
    data = fields.Nested(ProductSchema)


class ProductCreateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.CREATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.CREATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.CREATE_ERROR.message)


class ProductCompleteUpdateRequestSchema(ProductCreateRequestSchema):
    pass


class ProductUpdateResponseSchema(ProductCreateResponseSchema):
    pass


class ProductUpdateErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.UPDATE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.UPDATE_ERROR.label)
    message = fields.Str(example=MessagesEnum.UPDATE_ERROR.message)


class ProductSoftUpdateRequestSchema(Schema):
    field = fields.Str(example="value")


class ProductSoftDeleteResponseSchema(DefaultResponseSchema):
    data = fields.Dict(example={"deleted": True})


class ProductDeleteResponseSchema(Schema):
    data = fields.Dict(example={"deleted": True})


class ProductSoftDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.SOFT_DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.SOFT_DELETE_ERROR.message)


class ProductDeleteErrorResponseSchema(ErrorSchema):
    code = fields.Int(example=MessagesEnum.DELETE_ERROR.code, required=True)
    label = fields.Str(example=MessagesEnum.DELETE_ERROR.label)
    message = fields.Str(example=MessagesEnum.DELETE_ERROR.message)

# ***************************
# Event
# ***************************


class EventSchema(Schema):
    type = fields.Str()
    data = fields.Dict()
    date = fields.DateTime(example="2021-05-03T19:41:36.315842-03:00")
    hash = fields.Str(example="406cce9743906f7b8d7dd5d5c5d8c95d820eeefd72a3a554a4a726d022d8fa19")

class EventCreateRequestSchema(EventSchema):
    pass

class EventUpdateRequestSchema(EventCreateRequestSchema):
    pass


class EventListResponseSchema(DefaultResponseSchema):
    data = fields.List(fields.Nested(EventSchema))
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventListErrorResponseSchema(ErrorSchema):
    pass


class EventGetResponseSchema(Schema):
    data = fields.Nested(EventSchema)
    control = fields.Nested(RequestControlSchema)
    meta = fields.Nested(MetaSchema)
    links = fields.List(fields.Nested(LinkSchema))


class EventCreateResponseSchema(Schema):
    result = fields.Bool(example=True)
    event_hash = fields.Str(example="c82bf3ee20dd2f4ae7109e52d313a3190f1a85ba3362c54d3eb6257bd0c4d69d")
    code = fields.Int(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.code)
    label = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.label)
    message = fields.String(example=MessagesEnum.EVENT_REGISTERED_WITH_SUCCESS.message)
    params = fields.List(fields.Str())


class EventCreateErrorResponseSchema(Schema):
    result = fields.Bool(example=False)
    event_hash = fields.Str(example=None)
    code = fields.Int(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.code)
    label = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.label)
    message = fields.String(example=MessagesEnum.EVENT_TYPE_UNKNOWN_ERROR.message)
    params = fields.List(fields.Str())


class EventUpdateResponseSchema(EventGetResponseSchema):
    pass


class EventDeleteResponseSchema(EventGetResponseSchema):
    data = fields.Nested(DeletionSchema)


def register():
    # simple function only to force the import of the script on app.py
    pass
