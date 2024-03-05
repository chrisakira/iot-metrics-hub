"""
Alchemy device Repository Module for Application
Version: 1.0.0
"""
from datetime import datetime

from application.request_control import Order, Pagination, PaginationType
from application.repositories.v1.alchemy import AbstractRepository
from application.vos.device import DeviceVO
from application.migrations.models import DeviceModel, DeviceLogModel
from sqlalchemy.ext.declarative import declarative_base 

# Definir o modelo
Base = declarative_base()

class DeviceModelBase(DeviceModel, Base):
    pass
class DeviceModelLogBase(DeviceLogModel, Base):
    pass

class DeviceRepository(AbstractRepository): 
    def __init__(self, logger=None, engine=None, alchemy_session=None):
        super().__init__(logger=None, engine=None, alchemy_session=None)
      
    def get(self, fields: list = None, device=None):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0 
        response = False  
        while(attempts < max_attempts): 
            try:
                self.alchemy_session = self.get_new_session()
                query = self.alchemy_session.query(DeviceModelBase) 
                if device is not None:
                    for field, value in device.to_dict().items():
                        query = query.filter(getattr(DeviceModelBase, field) == value)
                results = query.all()
                if results is None:
                    self.alchemy_session.close()
                    return response
                response = None
                for result in results: 
                    device = {}
                    for field in fields:
                        device[field] = result.__dict__[field] 
                    response = device
                self.alchemy_session.close()
                return response  
            except Exception as err:
                attempts += 1
                self.logger.error(err)
                self.logger.error(f"Attempt {attempts} of {max_attempts}")
                self.alchemy_session.close() 
        return response  
      
    def create(self, device: DeviceVO):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0  
        response = False  
        while(attempts < max_attempts):  
            self.alchemy_session = self.get_new_session() 
            new_device = DeviceModelBase(**device.to_dict()) 
            try:
                self.alchemy_session.add(new_device)  
                self.alchemy_session.commit() 
                self.alchemy_session.close()
                response = True  
                return response 
            except Exception as err:  
                attempts += 1 
                self.alchemy_session.rollback()  
                self.logger.error(err) 
                self.logger.error(f"Attempt {attempts} of {max_attempts}") 
                self.alchemy_session.close()
                
        return response  
       
    def update(self, device: DeviceVO, value, key=None):  
        max_attempts = self._MAX_ATTEMPTS 
        attempts = 0 
        response = False 
        while(attempts < max_attempts): 
             
            self.alchemy_session = self.get_new_session() 
            
            device_model = self.alchemy_session.query(DeviceModelBase).filter(getattr(DeviceModelBase, key) == value).first()

            if device_model:
                 
                for k, v in device.to_dict().items():
                    setattr(device_model, k, v)

                try:
                    self.alchemy_session.commit()
                    self.alchemy_session.close()
                    response = True
                    return response
                except Exception as err:
                    attempts += 1 
                    self.alchemy_session.rollback()
                    self.alchemy_session.close() 
                    self.logger.error(err)
                    self.logger.error(f"Attempt {attempts} of {max_attempts}") # Log the number of attempts 
            else: 
                self.alchemy_session.close()
                break

        return response  
    
    def ping(self, value=None, key=None):
        max_attempts = self._MAX_ATTEMPTS
        attempts = 0  
        while(attempts < max_attempts): 
            self.alchemy_session = self.get_new_session()  
            device = self.alchemy_session.query(DeviceModelBase).filter(DeviceModelBase.__dict__[key] == value).first() # Query the database for the device
            if device: 
                device.last_seen = datetime.now() 
                try:
                    self.alchemy_session.commit()          
                    self.alchemy_session.close()         
                    return True
                except Exception as err: 
                    attempts += 1 
                    self.logger.error(err)
                    self.logger.error(f"Attempt {attempts} of {max_attempts}") 
                    self.alchemy_session.rollback()
                    self.alchemy_session.close()
                    
      
        return device  
    
    def log_error(self, device: DeviceVO):
        max_attempts = self._MAX_ATTEMPTS
        attempts = 0
        response = False
        while(attempts < max_attempts):
            self.alchemy_session = self.get_new_session()
            if "timestamp" not in device.to_dict():
                device.timestamp = datetime.now()
            new_error_msg = DeviceModelLogBase(**device.to_dict())
            try:
                self.alchemy_session.add(new_error_msg)
                self.alchemy_session.commit()
                self.alchemy_session.close()
                response = True
                return response
            except Exception as err:
                attempts += 1
                self.alchemy_session.rollback()
                self.logger.error(err)
                self.logger.error(f"Attempt {attempts} of {max_attempts}")
                self.alchemy_session.close()
        return response

    def delete(self, device: DeviceVO, value, key=None):
        max_attempts = self._MAX_ATTEMPTS
        attempts = 0
        response = False
        while(attempts < max_attempts):
            self.alchemy_session = self.get_new_session() 
            device_to_delete = self.alchemy_session.query(DeviceModelBase).filter(getattr(DeviceModelBase, key) == value).first()
            if device_to_delete:
                try:
                    self.alchemy_session.delete(device_to_delete)
                    self.alchemy_session.commit()
                    self.alchemy_session.close()
                    response = True
                    return response
                except Exception as err:
                    attempts += 1
                    self.alchemy_session.rollback()
                    self.logger.error(err)
                    self.logger.error(f"Attempt {attempts} of {max_attempts}")
                    self.alchemy_session.close()
            else:
                response = False
                return response
        return response
   
    def list(self, fields: list = None, device=None):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0 
        response = False  
        while(attempts < max_attempts): 
            try:
                self.alchemy_session = self.get_new_session()
                query = self.alchemy_session.query(DeviceModelBase) 
                if device is not None:
                    for field, value in device.to_dict().items():
                        query = query.filter(getattr(DeviceModelBase, field).like(f"%{value}%"))
                results = query.all()
                if results is None:
                    self.alchemy_session.close()
                    return response
                response = []
                for result in results: 
                    device = {}
                    for field in fields:
                        device[field] = result.__dict__[field] 
                    response.append(device)
                self.alchemy_session.close()
                return response  
            except Exception as err:
                attempts += 1
                self.logger.error(err)
                self.logger.error(f"Attempt {attempts} of {max_attempts}")
                self.alchemy_session.close() 
        return response  
     