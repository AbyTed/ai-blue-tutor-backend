from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore

Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    
    
    username = Column("username",String, unique=True, nullable=False, primary_key = True)
    email = Column("email",String, unique=True, nullable=False)
    password = Column("passwords", String, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
    def __repr__(self):
        return f'<User {self.username} {self.username}>'
    

engine = create_engine("sqlite:///data/site.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


    
