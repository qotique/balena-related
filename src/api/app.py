import logging
import platform
import re
import socket
import uuid
from typing import Union, Optional

import psutil
from fastapi import FastAPI

from src.rick import GetCharacter, GetLocation, GetEpisode

api = FastAPI()


@api.get('/')
async def home():
    return {'hello': 'world'}


@api.get('/info')
def info():
    return get_system_info()


@api.get('/character')
async def character(
        name: Optional[Union[str, None]] = None,
        status: Optional[Union[str, None]] = None,
        species: Optional[Union[str, None]] = None,
        type: Optional[Union[str, None]] = None,
        gender: Optional[Union[str, None]] = None,
):
    result = await GetCharacter(
        name=name,
        status=status,
        species=species,
        type_=type,
        gender=gender,
    ).run_query()
    return result


@api.get('/location')
async def location(
        name: Optional[Union[str, None]] = None,
        type: Optional[Union[str, None]] = None,
        dimension: Optional[Union[str, None]] = None,
):
    result = await GetLocation(
        name=name,
        type_=type,
        dimension=dimension,
    ).run_query()
    return result


@api.get('/episode')
async def episode(
        name: Optional[Union[str, None]] = None,
        episode: Optional[Union[str, None]] = None,
):
    result = await GetEpisode(
        name=name,
        episode=episode,
    ).run_query()
    return result


@api.get('/characters')
async def characters():
    result = await GetCharacter().run_query()
    return result


@api.get('/locations')
async def locations():
    result = await GetLocation().run_query()
    return result


def get_system_info():
    try:
        info = {'platform': platform.system(), 'platform-release': platform.release(),
                'platform-version': platform.version(), 'architecture': platform.machine(),
                'hostname': socket.gethostname(), 'ip-address': socket.gethostbyname(socket.gethostname()),
                'mac-address': ':'.join(re.findall('../..', '%012x' % uuid.getnode())),
                'processor': platform.processor(),
                'ram': str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"}
        return info
    except Exception as e:
        logging.exception(e)



