from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine('sqlite:///music.db', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    songs = relationship('Song', secondary='link')


class Song(Base):
    __tablename__ = 'Song'
    id = Column(String, primary_key=True)
    name = Column(String)
    artist = Column(String)
    logoResource = Column(String)
    users = relationship('User', secondary='link')

class Link(Base):
   __tablename__ = 'link'
   user_id = Column(
      Integer,
      ForeignKey('User.id'),
      primary_key = True)
   song_id = Column(
   String,
   ForeignKey('Song.id'),
   primary_key = True)
   added_at = Column(String)
