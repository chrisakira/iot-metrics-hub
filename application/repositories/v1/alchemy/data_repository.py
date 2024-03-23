"""
Alchemy data Repository Module for Application
Version: 1.0.0
"""
from datetime import datetime

from application.request_control import Order, Pagination, PaginationType
from application.repositories.v1.alchemy import AbstractRepository
from application.vos.data import DataVO 
from application.migrations.models import MeasurementData
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()

class DeviceModelBase(MeasurementData, Base):
    pass
# Definir o modelo 
class DataRepository(AbstractRepository): 
    def __init__(self, logger=None, engine=None, alchemy_session=None):
        super().__init__(logger=None, engine=None, alchemy_session=None)
    
    def create(self, data: DataVO):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0  
        response = False  
        while(attempts < max_attempts):  
            self.alchemy_session = self.get_new_session() 
            new_data = DeviceModelBase(**data.to_dict()) 
            try:
                self.alchemy_session.add(new_data)  
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
     