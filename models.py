from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    searches = relationship('Search', back_populates='user')

class Search(Base):
    __tablename__ = 'searches'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    city = Column(String, index=True)
    user = relationship('User', back_populates='searches')

Base.metadata.create_all(engine)
