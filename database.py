from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "mysql+pymysql://appuser:App%401234@127.0.0.1:3307/culture_portal"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)

Base = declarative_base()

