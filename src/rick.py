import asyncio
import logging
import time
from abc import abstractmethod, ABC
from pprint import pprint
from typing import Dict, List, Union
from pydantic import BaseModel
import requests

BASE_URL = 'https://rickandmortyapi.com/api'

__all__ = ['Character', 'Episode', 'Location', 'BASE_URL']


class Model(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item]


class Character(Model):
    id: int
    name: str
    status: str
    species: str
    type: str
    origin: Dict[str, str]
    location: Dict[str, str]
    image: str
    episode: List[str]
    url: str
    created: str
    link: Union[str, None]
    episodes: Union[int, None]

class Location(Model):
    id: int
    name: str
    type: str
    dimension: str
    residents: List[str]
    url: str
    created: str


class Episode(Model):
    id: int
    name: str
    air_date: str
    episode: str
    characters: List[Union[str, None]]
    url: str
    created: str
    link: Union[str, None]


class Url:
    url: str = None


class RequestParamsBuilder(Url):

    @staticmethod
    def build_params(kwargs: Dict[str, Union[str, None]]):
        params: str = ''
        first = True
        for name, value in kwargs.items():
            if value:
                params += f'{name}={value}' if first else f'&{name}={value}'
                first = False
        return params

    @abstractmethod
    async def run_query(self):
        global response
        response = self.get_entity()

    @abstractmethod
    def get_entity(self):
        response = requests.get(self.url, headers={'User-agent': 'your bot 0.1'}).json()
        error = response.get('error', None)
        if error:
            return response
        return response['results']


class GetCharacter(RequestParamsBuilder, ABC):
    def __init__(
            self,
            name: str = None,
            status: str = None,
            species: str = None,
            type_: str = None,
            gender: str = None
    ):
        url = f'{BASE_URL}/character/?'
        params = self.build_params(
            dict(
                name=name,
                status=status,
                species=species,
                type=type_,
                gender=gender
            )
        )

        self.url = url + params

    async def run_query(self):
        response_ = requests.get(self.url)
        if response_.status_code == 429:
            time.sleep(10)
            await self.run_query()
        response_json = response_.json()
        result = []
        result.extend(response_json['results'])
        while response_json['info']['next']:
            response_json = requests.get(response_json['info']['next']).json()
            result.extend(response_json['results'])
        characters = []
        for item in result:
            character = Character(**item)
            character.link = f'character/{character.id}'
            character.episodes = len(character.episode)
            characters.append(character)
        return characters

    def get_character_by_id(self, id: int):
        self.url = f'{BASE_URL}/character/{id}'
        response = requests.get(
            self.url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        if response.status_code == 429:
            time.sleep(10)
            self.get_character_by_id(id)
        obj = response.json()
        character = Character(**obj)
        character.link = f'character{id}'
        return character


class GetLocation(RequestParamsBuilder, ABC):
    def __init__(
            self,
            name: str = None,
            type_: str = None,
            dimension: str = None,
    ):
        url = f'{BASE_URL}/location/?'
        parameters = self.build_params(
            dict(
                name=name,
                type=type_,
                dimension=dimension
            )
        )
        self.url = url + parameters

    async def run_query(self):
        await super(GetLocation, self).run_query()
        if len(response) == 1:
            try:
                return Location(**response[0])
            except KeyError as error:
                logging.error(error)
                return response
        locations = []
        for location in response:
            location = Location(**location)
            locations.append(location)
        return locations


class GetEpisode(RequestParamsBuilder, ABC):
    def __init__(
            self,
            name: str = None,
            episode: str = None
    ):
        url = f'{BASE_URL}/episode/?'
        parameters = self.build_params(
            dict(
                name=name,
                episode=episode
            )
        )
        self.url = url + parameters

    async def run_query(self):
        await super(GetEpisode, self).run_query()
        if len(response) == 1:
            try:
                return Episode(**response[0])
            except KeyError as error:
                logging.error(error)
                return response
        episodes = []
        for episode in response:
            episode = Episode(**episode)
            episodes.append(episode)
        return episodes

    def get_episode_by_id(self, id: int):
        self.url = f'{BASE_URL}/episode/{id}'
        response = requests.get(
            self.url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        if response.status_code == 429:
            time.sleep(10)
            self.get_episode_by_id(id)
        obj = response.json()
        episode = Episode(**obj)
        episode.link = f'episode{id}'
        return episode

    def get_episode_by_url(self, url: str):
        response = requests.get(url)
        return Episode(**response.json())

# async def main():
#     request = await GetEpisode().get_episode_by_id(1)
#     return request
#
#
# if __name__ == '__main__':
#     items = asyncio.run(main())
#     for item in items:
#         print(item)
