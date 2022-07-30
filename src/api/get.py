import string
from typing import Optional, Union

from pydantic import BaseModel
from sqlalchemy import and_, text
from sqlalchemy.orm import aliased

from db.engine import DataBase
from db.schemas import Character, Location, Episode
from src.config import DB_URL


class Model(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item]


class Get:

    @staticmethod
    def characters(
            name: Optional[Union[str, None]] = None,
            status: Optional[Union[str, None]] = None,
            species: Optional[Union[str, None]] = None,
            type_: Optional[Union[str, None]] = None,
            gender: Optional[Union[str, None]] = None,
    ):
        class CharacterRepresentation(Model):
            hash: str
            id: int
            name: str
            status: str
            species: str
            type_: str
            origin: str
            location: str
            image: str
            episodes: str
            url: str
            created: str
            link: str
            episodes: str

        db = DataBase(DB_URL)
        keywords = {
            'name': name,
            'status': status,
            'species': species,
            'type': type_,
            'gender': gender
        }
        model_mapping = {
            'name': Character.name,
            'status': Character.status,
            'species': Character.species,
            'type': Character.type,
            'gender': Character.gender,
        }
        keywords_ = {model_mapping[k]: v for k, v in keywords.items() if v}
        print(keywords_)
        whereclause = and_((k.like(f'%{v}') for k, v in keywords_.items()))
        print(whereclause)
        with db.session() as session:
            sql_string = f"""
            select characters.hash,
            characters.id,
            characters.name,
            characters.status,
            characters.type,
            characters.species,
            l.name as origin,
            l2.name as location
            from characters
            join locations l on origin = l.hash
            join locations l2 on location = l2.hash
            """
            print(sql_string)
            characters = session.execute(sql_string).filter(whereclause).all()

        for idx, character in enumerate(characters):
            characters[idx] = CharacterRepresentation()
        return characters

    @staticmethod
    def locations(
            name: Optional[Union[str, None]] = None,
            dimension: Optional[Union[str, None]] = None,
            type_: Optional[Union[str, None]] = None,
    ):
        db = DataBase(DB_URL)
        keywords = {
            'name': name,
            'dimension': dimension,
            'type': type_,
        }
        model_mapping = {
            'name': Location.name,
            'dimension': Location.dimension,
            'type': Location.type,
        }
        keywords = {model_mapping[k]: v for k, v in keywords.items() if v}
        whereclause = and_((k.like(f'%{v}') for k, v in keywords.items()))
        with db.session() as session:
            locations_query = session.query(
                Location
            ).filter(whereclause)
            locations = locations_query.all()
            for location in locations:
                print(location.name)
        return locations

    @staticmethod
    def episodes(
            name: Optional[Union[str, None]] = None,
            episode: Optional[Union[str, None]] = None,
    ):
        db = DataBase(DB_URL)
        keywords = {
            'name': name,
            'episode': episode,
        }
        model_mapping = {
            'name': Episode.name,
            'episode': Episode.episode,
        }
        keywords = {model_mapping[k]: v for k, v in keywords.items() if v}
        whereclause = and_((k.like(f'%{v}') for k, v in keywords.items()))
        with db.session() as session:
            episodes_query = session.query(
                Episode
            ).filter(whereclause)
            episodes = episodes_query.all()
            for episode in episodes:
                print(episode.name)
        return episodes

    @staticmethod
    def character(id_: int):
        db = DataBase(DB_URL)
        with db.session() as session:
            character_query = session.query(Character).filter(Character.id == id_)
            character = character_query.first()
        return character


if __name__ == '__main__':
    Get.characters(name='rick', status='dead', type_='clone')
    Get.locations(name='earth')
    Get.episodes(episode='s01e01')
