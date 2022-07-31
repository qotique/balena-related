from sqlalchemy import Column, Integer, String

from db.schemas import Base


__all__ = ('Episode',)


class Episode(Base):
    __tablename__ = 'episodes'
    __table_args__ = {'extend_existing': True}
    hash = Column('hash', String(128), primary_key=True)
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(255))
    air_date = Column('air_date', String(128))
    episode = Column('episode', String(128))
    characters = Column('characters', String)
    url = Column('url', String(255))
    created = Column('created', String(128))
    link = Column('link', String(128))
