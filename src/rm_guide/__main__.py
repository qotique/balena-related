import uuid
from typing import List, Dict, Optional, Union

import requests

from db.engine import DataBase
from db.schemas import *
from src.config import DB_URL
from src.rick import BASE_URL


def get_uuid_hex():
    return uuid.uuid4().hex


class RickAndMortyGuide:
    def __init__(self):
        self.db = DataBase(DB_URL)
        self.api_url: str = BASE_URL

        self.cache = {}
        self.raw_characters = {}
        self.raw_locations = {}
        self.raw_episodes = {}
        self.init_db()

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

    def init_db(self):
        with self.db.session() as session:
            self.init_characters(session)
            self.init_locations(session)
            self.init_episodes(session)
            self.normalize_locations(session)

    def init_characters(self, session):
        raw_characters_list = self.get_raw_data('character')
        for item in raw_characters_list:
            hash_hex = get_uuid_hex()
            item['url'] = item['url'].replace(self.api_url, '')
            self.raw_characters[hash_hex] = item

    def init_locations(self, session):
        raw_locations_list = self.get_raw_data('location')
        for item in raw_locations_list:
            hash_hex = get_uuid_hex()
            item['url'] = item['url'].replace(self.api_url, '')
            self.raw_locations[hash_hex] = item

    def init_episodes(self, session):
        raw_episodes_list = self.get_raw_data('episode')
        for item in raw_episodes_list:
            hash_hex = get_uuid_hex()
            item['url'] = item['url'].replace(self.api_url, '')
            self.raw_episodes[hash_hex] = item

    def normalize_locations(self, session):
        """"""
        def find_location_hash(name):
            for location_hash, location in self.raw_locations.items():
                if location['name'] == name:
                    return location_hash

        def find_episode_hash(episode_id):
            for episode_hash, episode in self.raw_episodes.items():
                if int(episode['id']) == int(episode_id):
                    return episode_hash

        def find_character_hash(character_id):
            for character_hash, character in self.raw_characters.items():
                if int(character['id']) == int(character_id):
                    return character_hash

        for character_hash, character_dict in self.raw_characters.items():
            origin_idx = character_dict['origin']['url'].replace(f'{self.api_url}/location/', '')
            origin_name = character_dict['origin']['name']
            location_name = character_dict['location']['name']
            character_dict['origin'] = find_location_hash(origin_name)
            character_dict['location'] = find_location_hash(location_name)
            for idx, episode_url in enumerate(character_dict['episode']):
                episode_id = episode_url.replace(f'{self.api_url}/episode/', '')
                character_dict['episode'][idx] = find_episode_hash(episode_id)
            character_dict['episode'] = ','.join(character_dict['episode'])
            character_object = Character(hash=character_hash, **character_dict)
            session.add(character_object)
        session.commit()
        print('Normalized and loaded characters')

        for episode_hash, episode_dict in self.raw_episodes.items():
            for idx, character_url in enumerate(episode_dict['characters']):
                character_id = character_url.replace(f'{self.api_url}/character/', '')
                episode_dict['characters'][idx] = find_character_hash(character_id)
            episode_dict['characters'] = ','.join(episode_dict['characters'])
            episode_object = Episode(hash=episode_hash, **episode_dict)
            session.add(episode_object)
        session.commit()
        print('Normalized and loaded episodes')

        for location_name, location_dict in self.raw_locations.items():
            for idx, character_url in enumerate(location_dict['residents']):
                character_id = character_url.replace(f'{self.api_url}/character/', '')
                location_dict['residents'][idx] = find_character_hash(character_id)
            location_dict['residents'] = ','.join(location_dict['residents'])
            location_object = Location(hash=location_name, **location_dict)
            session.add(location_object)
        session.commit()
        print('Normalized and loaded locations')


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
    for idx, item in enumerate(chars):
        for key, value in keywords.items():
            print(item[key].lower() == value.lower())
            if item[key].lower() != value.lower():
                chars.pop(idx)
    return chars


if __name__ == '__main__':
    app = RickAndMortyGuide()
