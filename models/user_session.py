from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base


class UserSession(Base):

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    refresh_token = Column(String)

    ip_address = Column(String)

    browser = Column(String)

    device = Column(String)

    login_time = Column(DateTime)

    logout_time = Column(DateTime)

    session_expiry = Column(DateTime)

    status = Column(String)
