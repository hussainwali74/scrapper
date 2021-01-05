from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://db_dev:lolpass@localhost/scrapper_db"
SQLALCHEMY_DATABASE_URL = "postgres://fmihrwoqyljazr:6d3971e99cf3a27c3762cea7c0bd918c7f65a0210ad9da6e6d603f58d3d57f04@ec2-3-210-255-177.compute-1.amazonaws.com:5432/d13hhdsa2jq3un"

engine = create_engine( SQLALCHEMY_DATABASE_URL )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
