from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(
        String, default="This person prefers to keep an air of mystery"
    )
    signup_email_success = Column(Boolean, default=False)
