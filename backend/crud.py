from typing import List, Optional, TypeVar
from sqlmodel import Session, select
from backend.database.database import YourModel  # Replace with your actual model(s)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generic type for model classes
ModelType = TypeVar("ModelType", bound=YourModel)  # Replace `YourModel` with your base model if needed


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
        """
        logger.info(f"Fetching {self.model.__name__} record with ID: {id}.")
        try:
            obj = session.get(self.model, id)
            if not obj:
                logger.warning(f"{self.model.__name__} record with ID {id} not found.")
            return obj
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} record: {e}")
            raise

    def get_all(self, session: Session) -> List[ModelType]:
        """
        Retrieve all records of the model.
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
            logger.error(f"Error updating {self.model.__name__} record: {e}")
            raise

    def delete(self, session: Session, id: int) -> Optional[ModelType]:
        """
        Delete a record by its ID.
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
            logger.error(f"Error deleting {self.model.__name__} record: {e}")
            raise


# Example usage of the CRUD class
your_model_crud = CRUD(YourModel)  # Replace `YourModel` with your actual model