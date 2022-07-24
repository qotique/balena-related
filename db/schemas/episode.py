from sqlalchemy import Column, Integer, String, ARRAY, PickleType

from db.schemas import Base


__all__ = ('Episode',)


class Episode(Base):
    __tablename__ = 'episodes'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    air_date = Column(String(128))
    episode = Column(String(128))
    characters = Column(PickleType)
    url = Column(String(255))
    created = Column(String(128))
    link = Column(String(128))
