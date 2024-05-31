#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database.

        Args:
            email (str): The user's email address.
            hashed_password (str): The user's hashed password.

        Returns:
            User: The newly created User object.
        """
        new_user = User(email=email, hashed_password=hashed_password)
        try:
            self._session.add(new_user)
            self._session.commit()
            return new_user
        except Exception as e:
            self._session.rollback()
            raise e

    def find_user_by(self, **kwargs) -> User:
        """Takes keyword args and returns the first row found in the users
        table as filtered by the method's inputed arguments.
        """
        if not kwargs:
            raise InvalidRequestError("No arguments provided")

        for key in kwargs:
            if not hasattr(User, key):
                raise InvalidRequestError(f"Invalid attribute: {key}")

        query = self._session.query(User)
        for key, value in kwargs.items():
            query = query.filter(getattr(User, key) == value)

        user = query.first()

        if user is None:
            raise NoResultFound("No user found with the given criteria")

        return user
