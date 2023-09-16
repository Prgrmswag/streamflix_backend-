import json
import os
from dataclasses import dataclass

import requests
import uvicorn
from decouple import config
from ezflix import Ezflix
from fastapi import FastAPI
from pydantic import BaseModel
from pyngrok import ngrok
from tmdbv3api import Movie, TMDb, Search
from torrentp import TorrentDownloader

app = FastAPI()
tmdb = TMDb()
tmdb.api_key = config('TMDB_API')
ngrok.set_auth_token(config('NGROK_TOKEN'))
print(ngrok.connect('8000').public_url)


class SearchModel(BaseModel):
    q: str


@dataclass
class Movie:
    id: int
    title: str
    description: str
    date: str
    popularity: float
    vote: float
    voteCount: int
    posterImage: str
    wallpaperImage: str

    @staticmethod
    def from_json(json_map):
        return Movie(
            id=json_map['id'],
            title=json_map['original_title'],
            description=json_map['overview'],
            date=json_map['release_date'],
            popularity=json_map['popularity'],
            vote=json_map['vote_average'],
            voteCount=json_map['vote_count'],
            posterImage=json_map['poster_path'],
            wallpaperImage=json_map['backdrop_path'],
        )


@app.get("/popular-movies")
async def popular_movies():
    movie = Movie()
    popular = movie.popular()
    results = popular.get('results')
    movies = []
    for res in results:
        movies.append(Movie.from_json(res))
    return {"data": movies}


@app.get("/discover-movies")
async def discover_movies():
    movie = Movie()
    top_rated = movie.top_rated()
    results = top_rated.get('results')
    movies = []
    for res in results:
        movies.append(Movie.from_json(res))
    return {"data": movies}


@app.post("/search-movies")
async def search_endpoint(data: SearchModel):
    search_term = data.q
    search = Search()
    search_results = search.movies(search_term)
    results = search_results.get('results')
    movies = []
    for res in results:
        movies.append(Movie.from_json(res))
    return {"data": movies}


@app.post("/details")
async def details_endpoint(data: SearchModel):
    tmdb_id = data.q
    movie = Movie()
    details = movie.details(tmdb_id)

    ezflix = Ezflix(query='Goodfellas', media_type='movie', quality='720p', limit=1)
    movies = ezflix.search()
    details['link'] = movies[0]['link']
    return json.dumps(dict(details))


@app.get("/download")
async def details_endpoint(data: SearchModel):
    link = data.q
    with open("download.torrent", "wb") as f:
        r = requests.get(link)
        f.write(r.content)
    os.mkdir('download-contents')
    torrent_file = TorrentDownloader("download.torrent", './download-contents/')
    torrent_file.start_download()
    return json.dumps({"status": True})


if __name__ == "__main__":
    uvicorn.run(app)
