from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class FailedLogin(Base):

    __tablename__ = "failed_logins"

    id = Column(Integer, primary_key=True)

    email = Column(String)

    ip_address = Column(String)

    attempt_time = Column(DateTime)
