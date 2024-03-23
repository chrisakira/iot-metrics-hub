"""
Device Value Object Module for Application
Version: 1.0.0
"""
import uuid

from application.helper import datetime_now_with_timezone
from application.vos import AbstractVO
from datetime import datetime
from asammdf import MDF 
import re

date_time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
class DataVO(AbstractVO):
    """

    """
    def convert_value(self, value):
        converters = {
            int:        lambda x: int(x),
            datetime:   lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z") if date_time_pattern.match(x) else str(x),
            str:        lambda x: str(x)
        }

        for type_, converter in converters.items():
            try:
                return converter(value)
            except (ValueError, TypeError):
                pass

        return value

    def __init__(self, data: dict = None, default_values=True):
        """
        Always the dateobjects must be datetime instances
        """
        if data is not None:
            for key, value in data.items():
                for key, value in data.items():
                    setattr(self, f"{key.replace(';', '')}", self.convert_value(value))
    
    def Array(self, request, debug=False):
        """
        Returns an array of tuples from the request data.

        Args:
            request (dict): The request data.
            debug (bool, optional): Whether to print debug information or not. Defaults to False.

        Returns:
            list: An array of tuples.
        """
        valores = []
        for chave, lista_valores in request["data"].items():
            for valor in lista_valores:
                valores.append((chave, valor))
        if debug:
            atributos = vars(self)  # Obtém todos os atributos da instância
            for nome, valor in atributos.items():
                print(f"Nome da variável: {nome}, Valor da variável: {valor}")
        return valores

    def MF4_Loader_Types(self, mdf: MDF, debug=False):
        """
        Loads the types for the MF4 file.

        Args:
            mdf (MDF): The MDF file.
            debug (bool, optional): Whether to print debug information or not. Defaults to False.
        """ 
        group = 0
        for channel in mdf.iter_channels(False):
            if channel.group_index == group:
                setattr(self, f"`timestamp_CG_{channel.group_index}`", "BIGINT")
                group += 1
            setattr(self, f"`{channel.name.replace(';', '')}_CG_{channel.group_index}`", "INT")
        
        if debug:
            atributos = vars(self)  # Obtém todos os atributos da instância
            for nome, valor in atributos.items():
                print(f"Nome da variável: {nome}, Valor da variável: {valor}")
        return self

    def MF4_Loader_Data(self, mdf: MDF, debug=False):
        """
        Loads the data for the MF4 file.

        Args:
            mdf (MDF): The MDF file.
            debug (bool, optional): Whether to print debug information or not. Defaults to False.
        """
        group = 0 
        for channel in mdf.iter_channels():
            if channel.group_index == group:
                timestamps_ = channel.timestamps.tolist()
                new_timestamps = []
                for timestamp in timestamps_: 
                    new_timestamps.append(int(timestamp*1000 + mdf.start_time.timestamp()*1000))
    
                setattr(self, f"`timestamp_CG_{channel.group_index}`", new_timestamps)
                group += 1
            setattr(self, f"`{channel.name.replace(';', '')}_CG_{channel.group_index}`", channel.samples.tolist())
        if debug:
            for name, value in vars(self).items():
                print(f"Nome da variável: {name}, Valor da variável: {value}")
        return self
