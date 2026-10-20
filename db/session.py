from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from db.base import settings

# print(f"Database URL: {settings.DATABASE_URL}")
#Creating the SQLAlchemy engine using the database URL from settings
engine = create_engine(settings.DATABASE_URL, pool_size=settings.Max_Connection, max_overflow=settings.Max_Overflow, pool_timeout= settings.timeout)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print(f"Successfully created SQLAlchemy engine with URL: {settings.DATABASE_URL}")

Base = declarative_base()
# print(settings.DATABASE_URL)