import asyncio
import logging
from abc import abstractmethod, ABC
from pprint import pprint
from typing import Dict, List, Union
from pydantic import BaseModel
import requests

BASE_URL = 'https://rickandmortyapi.com/api'


class Character(BaseModel):
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


class Location(BaseModel):
    id: int
    name: str
    type: str
    dimension: str
    residents: List[str]
    url: str
    created: str


class Episode(BaseModel):
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
        response = requests.get(self.url).json()
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
        print(self.url)

    async def run_query(self):
        await super(GetCharacter, self).run_query()
        if len(response) == 1:
            try:
                return Character(**response[0])
            except KeyError as error:
                logging.error(error)
                return response
        characters = []
        for character in response:
            character = Character(**character)
            characters.append(character)
        return characters


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
        print(self.url)

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
        print(self.url)

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

    async def get_episode_by_id(self, id: int):
        self.url = f'{BASE_URL}/episode/{id}'
        response = requests.get(self.url).json()
        episode = Episode(**response)
        episode.link = f'episode{id}'
        return episode


# async def main():
#     request = await GetEpisode().get_episode_by_id(1)
#     return request
#
#
# if __name__ == '__main__':
#     items = asyncio.run(main())
#     for item in items:
#         print(item)
