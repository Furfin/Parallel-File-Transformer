from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from tools.settings import settings


Base = declarative_base()
engine = create_engine(f"{settings.db}://{settings.db_login}:{settings.db_password}@{settings.db_host}/{settings.db_name}")
connection = engine.connect()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer(), primary_key=True)
    filename = Column(String(100), nullable=False)
    hash = Column(String(100), nullable=True, unique=True)
    created_on = Column(DateTime(), default=datetime.now)
    status = Column(Integer(), nullable=False, default=0)
    from_ = Column(String(100), nullable=False)
    to_ = Column(String(100), nullable=False)
    
def init_db():
    #"postgresql://postgres:postgres@localhost:8081/postgres"
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine
    
def get_s():
    Session = sessionmaker(bind=engine)
    return Session()