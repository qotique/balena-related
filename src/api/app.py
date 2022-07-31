import asyncio
import logging
import platform
import re
import socket
import threading
import uuid
from math import ceil
from typing import Union, Optional
import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.engine import DataBase
from src.api.get import Get
from src.config import DB_URL
from src.rick import GetCharacter, GetLocation, GetEpisode
from src.rm_guide import RickAndMortyGuide

api = FastAPI()
db = DataBase(DB_URL)
api.mount("/static", StaticFiles(directory="src/api/static"), name="static")

templates = Jinja2Templates(directory="src/api/templates")


@api.get('/', response_class=HTMLResponse)
async def home(request: Request):
    debug_info = {'running_on': platform.machine()}
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "debug_info": debug_info}
    )


@api.get('/info')
def info():
    return get_system_info()


@api.get('/characters', response_class=HTMLResponse)
async def characters(
        request: Request,
        name: Optional[Union[str, None]] = None,
        status: Optional[Union[str, None]] = None,
        species: Optional[Union[str, None]] = None,
        type: Optional[Union[str, None]] = None,
        gender: Optional[Union[str, None]] = None,
):
    characters = Get.characters(name, status, species, type, gender)
    # we need to ceil chars for rows and columns
    characters_rows = list(range(0, ceil(len(characters)/3)))

    return templates.TemplateResponse(
        "characters.html",
        {
            "request": request,
            "characters": characters,
            "characters_rows": characters_rows,
        }
    )


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


@api.get('/episode/{id}', response_class=HTMLResponse)
async def episode_by_id(
        request: Request,
        id: int,
):
    result = GetEpisode().get_episode_by_id(id)
    return templates.TemplateResponse('episode.html', {"request": request, "episode": result})


@api.get('/character/{id}', response_class=HTMLResponse)
async def character(
        request: Request,
        id: int
):
    character = Get.character(id)
    character.episodes = character.episode.split(',')
    character.episodes = [Get.episode(hash_) for hash_ in character.episodes]
    for episode in character.episodes:
        episode.episode = f'episodes/{episode.episode}.jpg'
    first_episode_hash = character.episode.split(',')[0]
    origin_hash = character.origin
    first_episode = Get.episode(first_episode_hash)
    first_episode.episode = f'episodes/{first_episode.episode}.jpg'
    origin = Get.location(origin_hash)
    return templates.TemplateResponse(
        'character.html', {
            "request": request,
            "character": character,
            "first_episode": first_episode,
            "origin": origin,
        }
    )


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


if __name__ == '__main__':
    uvicorn.run('src.api.app:api', reload=True)
