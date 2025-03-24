from typing import List, Optional, TypeVar
from sqlmodel import Session, select
from backend.database.models import SQLModel  # Base model for all SQLModel classes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generic type for model classes
ModelType = TypeVar("ModelType", bound=SQLModel)


class CRUD:
    """
    A generic CRUD class to handle common database operations.
    """

    def __init__(self, model: ModelType):
        """
        Initialize the CRUD instance with a specific SQLModel class.
        """
        self.model = model

    def create(self, session: Session, obj_in: ModelType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            session (Session): The database session.
            obj_in (ModelType): The object to be created.

        Returns:
            ModelType: The created object.
        """
        logger.info(f"Creating new {self.model.__name__} record.")
        try:
            session.add(obj_in)
            session.commit()
            session.refresh(obj_in)
            logger.info(f"{self.model.__name__} record created successfully.")
            return obj_in
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__} record: {e}")
            raise

    def get(self, session: Session, id: int) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.

        Args:
            session (Session): The database session.
            id (int): The ID of the record to retrieve.

        Returns:
            Optional[ModelType]: The retrieved object, or None if not found.
        """
        logger.info(f"Fetching {self.model.__name__} record with ID: {id}.")
        try:
            obj = session.get(self.model, id)
            if not obj:
                logger.warning(f"{self.model.__name__} record with ID {id} not found.")
            return obj
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} record with ID {id}: {e}")
            raise

    def get_all(self, session: Session) -> List[ModelType]:
        """
        Retrieve all records of the model.

        Args:
            session (Session): The database session.

        Returns:
            List[ModelType]: A list of all records.
        """
        logger.info(f"Fetching all {self.model.__name__} records.")
        try:
            statement = select(self.model)
            results = session.exec(statement).all()
            logger.info(f"Fetched {len(results)} {self.model.__name__} records.")
            return results
        except Exception as e:
            logger.error(f"Error fetching all {self.model.__name__} records: {e}")
            raise

    def update(self, session: Session, id: int, obj_in: dict) -> Optional[ModelType]:
        """
        Update an existing record by its ID.

        Args:
            session (Session): The database session.
            id (int): The ID of the record to update.
            obj_in (dict): A dictionary of fields to update.

        Returns:
            Optional[ModelType]: The updated object, or None if not found.
        """
        logger.info(f"Updating {self.model.__name__} record with ID: {id}.")
        try:
            obj = session.get(self.model, id)
            if not obj:
                logger.warning(f"{self.model.__name__} record with ID {id} not found.")
                return None
            for key, value in obj_in.items():
                setattr(obj, key, value)
            session.commit()
            session.refresh(obj)
            logger.info(f"{self.model.__name__} record updated successfully.")
            return obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} record with ID {id}: {e}")
            raise

    def delete(self, session: Session, id: int) -> Optional[ModelType]:
        """
        Delete a record by its ID.

        Args:
            session (Session): The database session.
            id (int): The ID of the record to delete.

        Returns:
            Optional[ModelType]: The deleted object, or None if not found.
        """
        logger.info(f"Deleting {self.model.__name__} record with ID: {id}.")
        try:
            obj = session.get(self.model, id)
            if not obj:
                logger.warning(f"{self.model.__name__} record with ID {id} not found.")
                return None
            session.delete(obj)
            session.commit()
            logger.info(f"{self.model.__name__} record deleted successfully.")
            return obj
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} record with ID {id}: {e}")
            raise