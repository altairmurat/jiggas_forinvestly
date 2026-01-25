from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class BaseModel(Base):
    __abstract__ = True
    __unmapped__ = True
    
    id = Column(Integer, primary_key=True)
    
class Zipfiles(BaseModel):
    __tablename__ = "zipfiles"
    
    friend_name = Column(String)
    content = Column(String)
    user_id = Column(ForeignKey("users.id")) #foreign key from users table called id
    
class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String)
    hashed_password = Column(String)
    zipfiles = relationship(Zipfiles) #relationship to zipfiles table AND user will have a LIST of zipfiles
    
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)      # ZIP filename
    response = Column(String)                 # GPT result