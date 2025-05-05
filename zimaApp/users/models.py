from sqlalchemy import JSON, VARCHAR, Column, DateTime, Integer, String

from zimaApp.database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    login_user = Column(String, nullable=False)
    name_user = Column(String, nullable=False)
    surname_user = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    position_id = Column(String, nullable=False)
    costumer = Column(String, nullable=False)
    contractor = Column(String, nullable=False)
    ctcrs = Column(String, nullable=False)
    password = Column(String, nullable=False)
    access_level = Column(String, nullable=False)


