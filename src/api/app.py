import asyncio
import logging
import platform
import re
import socket
import threading
import uuid
from typing import Union, Optional
import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.concurrency import run_in_threadpool

from src.rick import GetCharacter, GetLocation, GetEpisode

api = FastAPI()

api.mount("/static", StaticFiles(directory="src/api/static"), name="static")

templates = Jinja2Templates(directory="src/api/templates")


@api.get('/')
async def home():
    return {'hello': 'world'}


@api.get('/info')
def info():
    return get_system_info()


@api.get('/character', response_class=HTMLResponse)
async def character(
        request: Request,
        name: Optional[Union[str, None]] = None,
        status: Optional[Union[str, None]] = None,
        species: Optional[Union[str, None]] = None,
        type: Optional[Union[str, None]] = None,
        gender: Optional[Union[str, None]] = None,
):
    def set_episode_link(getter, item, idx, i):
        item.episode[idx] = getter(
            i.replace('https://rickandmortyapi.com/api/episode', '')
        )

    threads = []
    result = await GetCharacter(
        name=name,
        status=status,
        species=species,
        type_=type,
        gender=gender,
    ).run_query()

    for item in result:
        for idx, i in enumerate(item.episode):
            episode = GetEpisode()
            print(item, idx, i)
            thread = threading.Thread(
                target=set_episode_link,
                args=(episode.get_episode_by_id, item, idx, i)
            )
            thread.start()
            threads.append(thread)
    for thread_ in threads:
        thread_.join()
    return templates.TemplateResponse("characters.html", {"request": request, "characters": result})


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


if __name__ == '__main__':
    uvicorn.run('src.api.app:api', reload=True)
