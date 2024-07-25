from src import db
from src.persistence.file import FileRepository
import os

class DataManager:
    """
    DataManager class to handle data operations.

    This class provides an interface for saving, deleting, loading, and loading all instances of a class.
    It uses either a database (through SQLAlchemy) or a file repository for these operations, depending
    on the value of the USE_DATABASE environment variable.
    """

    def __init__(self):
        """
        Initialize DataManager instance.

        If the USE_DATABASE environment variable is set to 'True', use SQLAlchemy for data operations.
        Otherwise, use a FileRepository.
        """
        self.use_database = os.getenv('USE_DATABASE', 'False').lower() == 'true'
        if self.use_database:
            self.repo = None  # Use SQLAlchemy for database operations
        else:
            self.repo = FileRepository()

    def save(self, obj):
        """
        Save an object.

        If using a database, add the object to the current session and commit the session.
        If using a file repository, save the object to the repository.

        Args:
            obj: The object to save.
        """
        if self.use_database:
            db.session.add(obj)
            db.session.commit()
        else:
            self.repo.save(obj)

    def delete(self, obj):
        """
        Delete an object.

        If using a database, delete the object from the current session and commit the session.
        If using a file repository, delete the object from the repository.

        Args:
            obj: The object to delete.
        """
        if self.use_database:
            db.session.delete(obj)
            db.session.commit()
        else:
            self.repo.delete(obj)

    def load(self, cls, obj_id):
        """
        Load an object by its ID.

        If using a database, get the object with the given ID from the database.
        If using a file repository, get the object with the given ID from the repository.

        Args:
            cls: The class of the object to load.
            obj_id: The ID of the object to load.

        Returns:
            The object with the given ID, or None if no such object exists.
        """
        if self.use_database:
            return cls.query.get(obj_id)
        else:
            return self.repo.get(cls.__name__.lower(), obj_id)

    def load_all(self, cls):
        """
        Load all objects of a class.

        If using a database, get all objects of the class from the database.
        If using a file repository, get all objects of the class from the repository.

        Args:
            cls: The class of the objects to load.

        Returns:
            A list of all objects of the class.
        """
        if self.use_database:
            return cls.query.all()
        else:
            return self.repo.get_all(cls.__name__.lower())