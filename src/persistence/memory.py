"""
This module exports a Repository that does not persist data,
it only stores it in memory
"""

from datetime import datetime
from src.models.base import Base
from src.persistence.repository import Repository
#from populate import populate_db


class MemoryRepository(Repository):
    """
    A Repository that does not persist data, it only stores it in memory



    Every time the server is restarted, the data is lost
    """

    __data: dict[str, list] = {
        "user": [],
        "category": [],
        "item": [],
    }

    def __init__(self) -> None:
        """Calls reload method"""
        self.reload()

    def get_all(self, model_name: str) -> list:
        """Get all objects of a given model"""
        return self.__data.get(model_name, [])

    def get(self, model_name: str, obj_id: str):
        """Get an object by its ID"""
        for obj in self.get_all(model_name):
            if obj.id == obj_id:
                return obj
        return None

    def reload(self):
        """Populates the database with some dummy data"""
        #populate_db(self)

    def save(self, obj: Base):
        """Save an object"""
        cls = obj.__class__.__name__.lower()

        if obj not in self.__data[cls]:
            # print(f"Saving {obj}, {cls}")
            self.__data[cls].append(obj)

        return obj

    def update(self, obj: Base):
        """Update an object"""
        cls = obj.__class__.__name__.lower()

        for i, o in enumerate(self.__data[cls]):
            if o.id == obj.id:
                obj.updated_at = datetime.now()
                self.__data[cls][i] = obj
                return obj

        return None

    def delete(self, obj: Base) -> bool:
        """Delete an object"""
        cls = obj.__class__.__name__.lower()

        if obj in self.__data[cls]:
            self.__data[cls].remove(obj)
            return True

        return False