"""
Alchemy file Repository Module for Application
Version: 1.0.0
"""
from datetime import datetime

from application.request_control import Order, Pagination, PaginationType
from application.repositories.v1.alchemy import AbstractRepository
from application.vos.file import FileVO
from application.migrations.models import FileModel
from sqlalchemy.ext.declarative import declarative_base 

# Definir o modelo
Base = declarative_base()

class FileModelBase(FileModel, Base):
    pass

class FileRepository(AbstractRepository): 
    def __init__(self, logger=None, engine=None, alchemy_session=None):
        super().__init__(logger=None, engine=None, alchemy_session=None)
      
    def get(self, fields: list = None, file=None):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0 
        response = False  
        while(attempts < max_attempts): 
            try:
                self.alchemy_session = self.get_new_session()
                query = self.alchemy_session.query(FileModelBase) 
                if file is not None:
                    for field, value in file.to_dict().items():
                        query = query.filter(getattr(FileModelBase, field) == value)
                results = query.all()
                if results is None:
                    self.alchemy_session.close()
                    return response
                response = None
                for result in results: 
                    file = {}
                    for field in fields:
                        file[field] = result.__dict__[field] 
                    response = file
                self.alchemy_session.close()
                return response  
            except Exception as err:
                attempts += 1
                self.logger.error(err)
                self.logger.error(f"Attempt {attempts} of {max_attempts}")
                self.alchemy_session.close() 
        return response  
      
    def create(self, file: FileVO):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0  
        response = False  
        while(attempts < max_attempts):  
            self.alchemy_session = self.get_new_session() 
            new_file = FileModelBase(**file.to_dict()) 
            try:
                self.alchemy_session.add(new_file)  
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
       
    def update(self, file: FileVO, value, key=None):  
        max_attempts = self._MAX_ATTEMPTS 
        attempts = 0 
        response = False 
        while(attempts < max_attempts): 
             
            self.alchemy_session = self.get_new_session() 
            
            file_model = self.alchemy_session.query(FileModelBase).filter(getattr(FileModelBase, key) == value).first()

            if file_model:
                 
                for k, v in file.to_dict().items():
                    setattr(file_model, k, v)

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
    
    def delete(self, file: FileVO, value, key=None):
        max_attempts = self._MAX_ATTEMPTS
        attempts = 0
        response = False
        while(attempts < max_attempts):
            self.alchemy_session = self.get_new_session() 
            file_to_delete = self.alchemy_session.query(FileModelBase).filter(getattr(FileModelBase, key) == value).first()
            if file_to_delete:
                try:
                    self.alchemy_session.delete(file_to_delete)
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
   
    def list(self, fields: list = None, file=None):
        max_attempts = self._MAX_ATTEMPTS  
        attempts = 0 
        response = False  
        while(attempts < max_attempts): 
            try:
                self.alchemy_session = self.get_new_session()
                query = self.alchemy_session.query(FileModelBase) 
                if file is not None:
                    for field, value in file.to_dict().items():
                        query = query.filter(getattr(FileModelBase, field).like(f"%{value}%"))
                results = query.all()
                if results is None:
                    self.alchemy_session.close()
                    return response
                response = []
                for result in results: 
                    file = {}
                    for field in fields:
                        file[field] = result.__dict__[field] 
                    response.append(file)
                self.alchemy_session.close()
                return response  
            except Exception as err:
                attempts += 1
                self.logger.error(err)
                self.logger.error(f"Attempt {attempts} of {max_attempts}")
                self.alchemy_session.close() 
        return response  
     