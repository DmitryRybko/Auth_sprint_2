"""Main module of FastAPI app."""

# Standard libs imports
# import logging

# Third apps imports
from redis import asyncio as aioredis

from elasticsearch7 import AsyncElasticsearch

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import uvicorn

# Project imports
from api.v1 import film_api, genre_api, person_api
from core.config import settings
# from core.logger import LOGGING
from db import elastic
from db import redis

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    # Changing default JSON serializer to optimized version.
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """Magic method to run something when server is starting.

    It connects to redis and elasticsearch in event-loop.
    """
    redis.redis = aioredis.from_url(
        f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
        encoding='utf8',
        decode_responses=True
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}']
    )

    FastAPICache.init(RedisBackend(redis.redis), prefix='fastapi-cache')


@app.on_event('shutdown')
async def shutdown():
    """Magic method to run something when server is shutting down.

    It closes connections with databases during shutdown.
    """
    await redis.redis.close()
    await elastic.es.close()

# Connect routers to paths.
app.include_router(film_api.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genre_api.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(
    person_api.router, prefix='/api/v1/persons', tags=['persons']
)

if __name__ == '__main__':
    # The app can be run by `uvicorn main:app --host 0.0.0.0 --port 8001` cmd.
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001,
    )
