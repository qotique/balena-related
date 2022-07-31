from sqlalchemy import Column, Integer, String

from db.schemas import Base

__all__ = ('Character', )


class Character(Base):
    __tablename__ = 'characters'
    __table_args__ = {'extend_existing': True}
    hash = Column('hash', String(128), primary_key=True)
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(64))
    gender = Column('gender', String(255))
    status = Column('status', String(16))
    species = Column('species', String(255))
    type = Column('type', String(16))
    origin = Column('origin', String(64))
    location = Column('location', String(64))
    image = Column('image', String(255))
    episode = Column('episode', String)
    url = Column('url', String(255))
    created = Column('created', String(64))
    link = Column('link', String(255), nullable=True)
    episodes = Column('episodes', String(255), nullable=True)
