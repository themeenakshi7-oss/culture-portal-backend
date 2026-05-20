# from sqlalchemy import Column, Integer, String
# from database import Base

# class User(Base):

#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)

#     name = Column(String(100))

#     email = Column(String(100), unique=True)

#     password = Column(String(255))


from sqlalchemy import Column, Integer, String
from database import Base

from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    fullname = Column(String(100))

    designation = Column(String(100))

    email = Column(String(100), unique=True)

    mobile = Column(String(20))

    organization = Column(String(100))

    country = Column(String(100))

    password = Column(String(255))
