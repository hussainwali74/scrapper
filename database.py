from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getenv

ENV = getenv("ENV")

if ENV == "prod":
    SQLALCHEMY_DATABASE_URL = "postgres://wotlzujyqzemtl:a9b17b0c827e24c433235ca89a3c73ed88c64fac119e8621c2c262cf0c5f9833@ec2-52-44-46-66.compute-1.amazonaws.com:5432/dfqd9trqnt0upm"
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://db_dev:lolpass@localhost/scrapper_db"

engine = create_engine( SQLALCHEMY_DATABASE_URL )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
