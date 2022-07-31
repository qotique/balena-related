from sqlalchemy import Column, Integer, String

from db.schemas import Base


__all__ = ('Location',)


class Location(Base):
    __tablename__ = 'locations'
    __table_args__ = {'extend_existing': True}
    hash = Column('hash', String(128), primary_key=True)
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(64))
    type = Column('type', String(16))
    dimension = Column('dimension', String(64))
    residents = Column('residents', String)
    url = Column(String(255))
    created = Column('created', String(64))
