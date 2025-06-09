from sqlalchemy import JSON, VARCHAR, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from zimaApp.database import Base


class Users(Base):
    __tablename__ = "users"

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

    wells_repairs = relationship("WellsRepair", back_populates="users")
    norms_repairs = relationship("NormsWork", back_populates="users")

    def __repr__(self):
        return f"<Users(id={self.id}, login_user={self.login_user}, name_user={self.name_user}, " \
               f"surname_user={self.surname_user}, access_level={self.access_level})>"
