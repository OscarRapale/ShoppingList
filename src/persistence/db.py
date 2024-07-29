from src.models.base import Base
from src.models import db
from src.models.category import Category
from src.persistence.repository import Repository
from sqlalchemy.exc import SQLAlchemyError

class DBRepository(Repository):

    def __init__(self) -> None:
        
        self.__session = db.session
        self.reload()

    def get_all(self, model_name: str) -> list:
        
        try:
            return self.__session.query(model_name).all()
        except SQLAlchemyError:
            self.__session.rollback()
            return []
        
    def get(self, model_name: str, obj_id: str) -> Base | None:

        try:
            return self.__session.query(model_name).get(obj_id)
        except SQLAlchemyError:
            self.__session.rollback()
            return None
        
    def get_for_category(self, name: str) -> Base | None:

        try:
            return self.__session.query(Category).filter_by(name=name).first()
        except SQLAlchemyError:
            self.__session.rollback()
            return None
        
    def reload(self) -> None:
        
        self.__session = db.session

    def save(self, obj: Base) -> Base:

        try:
            self.__session.add(obj)
            self.__session.commit()
        except SQLAlchemyError as e:
            self.__session.rollback()
            print(f"Error saving object: {e}")

    def update(self, obj: Base) -> None:
        
        try:
            self.__session.commit()
        except SQLAlchemyError:
            self.__session.rollback()

    def delete(self, obj: Base) -> bool:
        
        try:
            self.__session.delete(obj)
            self.__session.commit()
        except SQLAlchemyError:
            self.__session.rollback()
            return False
        
    def _get_model_class(self, model_name: str):

        from src.models.user import User
        from src.models.category import Category
        from src.models.item import Item

        models = {
            'user': User,
            'category': Category,
            'item': Item
        }

        return models[model_name.lower()]
