"""
Alchemy data Repository Module for Application
Version: 1.0.0
"""
from datetime import datetime

from application.request_control import Order, Pagination, PaginationType
from application.repositories.v1.alchemy import AbstractRepository
from application.vos.data import DataVO 
from sqlalchemy.ext.declarative import declarative_base 

# Definir o modelo 
class DataRepository(AbstractRepository): 
    def __init__(self, logger=None, engine=None, alchemy_session=None):
        super().__init__(logger=None, engine=None, alchemy_session=None)
      