from sqlalchemy import Column, Integer, String, ARRAY, PickleType

from db.schemas import Base


__all__ = ('Location',)


class Location(Base):
    __tablename__ = 'locations'
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(64))
    type = Column('type', String(16))
    dimension = Column('dimension', String(64))
    residents = Column(PickleType)
    url = Column(String(255))
    created = Column('created', String(64))
