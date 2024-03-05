from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, TEXT, TIMESTAMP, text

REFERENCES = {}
MODELS = {}

class DeviceModel:
    __tablename__ = 'device'
    id =            Column(Integer,     primary_key=True,                                           name='id')
    name =          Column(String(255), nullable=False, default="Akira",                            name='name',        unique=True)
    mac_address =   Column(String(255), nullable=False, default="02:42:ac:11:22:33",                name='mac_address', unique=True)
    description =   Column(TEXT,        nullable=False, default="Device description",               name='description')
    active =        Column(Integer,     nullable=False, default=1,                                  name='active')
    status =        Column(Integer,     nullable=False, default=0,                                  name='status')
    model =         Column(String(255), nullable=False, default="ESP32",                            name='model')
    firmware =      Column(String(255), nullable=False, default="V0.0.1",                           name='firmware')
    last_seen =     Column(TIMESTAMP,   nullable=True,  server_default=text('CURRENT_TIMESTAMP'),   name='last_seen')
    created_at =    Column(TIMESTAMP,   nullable=False, server_default=text('CURRENT_TIMESTAMP'),   name='created_at')
    updated_at =    Column(TIMESTAMP,   nullable=False, server_default=text('CURRENT_TIMESTAMP'),   name='updated_at')
    deleted_at =    Column(TIMESTAMP,   nullable=True,  server_default=text('CURRENT_TIMESTAMP'),   name='deleted_at')
    delete_status = Column(Integer,     nullable=True,  default=0,                                  name='delete_status')
    
class DeviceLogModel:
    __tablename__ = 'device_log'
    id =            Column(Integer,     primary_key=True,                                           name='id')
    device_id =     Column(Integer,     nullable=False, default=0,                                  name='device_id')
    type =          Column(String(255), nullable=True,                                              name='type')
    message =       Column(TEXT,        nullable=True,                                              name='message')
    timestamp =     Column(TIMESTAMP,   nullable=False, server_default=text('CURRENT_TIMESTAMP'),   name='timestamp')
    
class ProductsModel:
    id = Column(Integer, primary_key=True, name='id')
    uuid = Column(String(60), nullable=False, name='uuid')
    sku = Column(Integer, nullable=False, name='sku')
    name = Column(String(255), nullable=False, name='name')
    description = Column(TEXT, nullable=False, name='description')
    supplier_id = Column(Integer, nullable=False, name='supplier_id')
    created_at = Column(TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP'), name='created_at')
    updated_at = Column(TIMESTAMP, nullable=True, name='updated_at')
    deleted_at = Column(TIMESTAMP, nullable=True, name='deleted_at')
    active = Column(Integer, default=1, name='active')


REFERENCES['device'] =      DeviceModel
REFERENCES['device_log'] =  DeviceLogModel 
REFERENCES['products'] =    ProductsModel


def create(db: SQLAlchemy):
    class Device(db.Model, DeviceModel):
        pass
    class DeviceLog(db.Model, DeviceLogModel):
        pass
    class Products(db.Model, ProductsModel):
        pass

    MODELS['device'] = Device
    MODELS['device_log'] = DeviceLog
    MODELS['products'] = Products
