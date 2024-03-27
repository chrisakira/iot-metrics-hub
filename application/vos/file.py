"""
File Value Object Module for Application
Version: 1.0.0
"""
import uuid

from application.helper import datetime_now_with_timezone
from application.vos import AbstractVO
from datetime import datetime
import re

date_time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
class FileVO(AbstractVO):
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
    