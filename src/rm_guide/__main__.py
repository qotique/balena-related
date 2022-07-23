
from typing import List, Dict, Optional, Union

import requests

from src.rick import *


class RickAndMortyGuide:
    def __init__(self):
        self.api_url: str = BASE_URL
        self.characters: Dict[int, Character] = self.init_characters()
        self.episodes: Dict[int, Episode] = self.init_episodes()
        self.locations: Dict[int, Location] = self.init_locations()

    def get_raw_data(self, entity_name: str):
        result = []
        url = f'{self.api_url}/{entity_name}'
        response = requests.get(url)
        response_json = response.json()
        result.extend(response_json['results'])
        while response_json['info']['next']:
            response_json = requests.get(response_json['info']['next']).json()
            result.extend(response_json['results'])
        return result

    def init_characters(self):
        raw_characters = self.get_raw_data('character')
        characters: Dict[int, Character] = {}
        for item in raw_characters:
            character = Character(**item)
            character.link = f'character/{character.id}'
            character.episodes = len(character.episode)
            characters[character.id] = character
        # self.characters = characters
        return characters

    def init_locations(self):
        raw_locations = self.get_raw_data('location')
        locations: Dict[int, Location] = {}
        for item in raw_locations:
            location = Location(**item)
            locations[location.id] = location
        # self.locations = locations
        return locations

    def init_episodes(self):
        raw_episodes = self.get_raw_data('episode')
        episodes: Dict[int, Episode] = {}
        for item in raw_episodes:
            episode = Episode(**item)
            episode.link = f'episode/{episode.id}'
            episodes[episode.id] = episode
        # self.episodes = episodes
        return episodes

    def guide_test(self):
        self.extend_characters()
        self.extend_episodes()

    def extend_characters(self):
        for idx, character in self.characters.items():
            for idx_, episode in enumerate(character.episode):
                character.episode[idx_] = self.episodes.get(int(episode.rsplit('/', 1)[1])) # noqa

    def extend_episodes(self):
        for idx, episode in self.episodes.items():
            for idx_, character in enumerate(episode.characters):
               episode.characters[idx_] = self.characters.get(int(character.rsplit('/', 1)[1]))

    def extend_locations(self):
        for idx, location in self.locations.items():
            for idx_, resident in enumerate(location.residents):
                location.residents[idx_] = self.characters.get(int(resident.rsplit('/', 1)[1]))


def get_characters(
        name: Optional[Union[str, None]] = None,
        status: Optional[Union[str, None]] = None,
        species: Optional[Union[str, None]] = None,
        type_: Optional[Union[str, None]] = None,
        gender: Optional[Union[str, None]] = None,
):
    keywords_ = {
        'name': name,
        'status': status,
        'species': species,
        'type': type_,
        'gender': gender,
    }
    keywords = {
        k: v for k, v in keywords_.items() if v
    }
    app = RickAndMortyGuide()
    chars = [char for char in app.characters.values()]
    print(len(chars))
    for idx, item in enumerate(chars):
        for key, value in keywords.items():
            print(item[key].lower() == value.lower())
            if item[key].lower() != value.lower():
                print(idx)
                chars.pop(idx)
    print(f'{len(chars)=}')
    return chars


if __name__ == '__main__':
    print(get_characters(name='rick', status='dead', type_='clone'))


