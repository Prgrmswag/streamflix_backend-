import os

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from tmdbv3api import Movie, TMDb, Search
from ezflix import Ezflix
from torrentp import TorrentDownloader
from decouple import config

import uvicorn

app = FastAPI()
tmdb = TMDb()
tmdb.api_key = config('TMDB_API')
movie = Movie()
search = Search()


class SearchModel(BaseModel):
    q: str


@app.get("/popular-movies")
async def popular_movies():
    popular = movie.popular()
    return popular


@app.get("/discover-movies")
async def discover_movies():
    top_rated = movie.top_rated()
    return top_rated


@app.get("/search-movies")
async def search_endpoint(data: SearchModel):
    search_term = data.q
    search_results = search.movies(search_term)
    return search_results


@app.get("/details")
async def details_endpoint(data: SearchModel):
    tmdb_id = data.q
    details = movie.details(tmdb_id)

    ezflix = Ezflix(query='Goodfellas', media_type='movie', quality='720p', limit=1)
    movies = ezflix.search()
    details['link'] = movies[0]['link']
    return details


@app.get("/download")
async def details_endpoint(data: SearchModel):
    link = data.q
    with open("download.torrent", "wb") as f:
        r = requests.get(link)
        f.write(r.content)
    os.mkdir('download-contents')
    torrent_file = TorrentDownloader("download.torrent", './download-contents/')
    torrent_file.start_download()
    return {"status": True}


if __name__ == "__main__":
    uvicorn.run(app)
