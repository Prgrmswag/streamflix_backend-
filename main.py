import json
import os
from dataclasses import dataclass

import requests
import uvicorn
from decouple import config
from ezflix import Ezflix
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok
from fastapi.responses import StreamingResponse
from tmdbv3api import Movie, TMDb, Search
from torrentp import TorrentDownloader
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()
future = None
currentLink = None
torrent_file = None
app = FastAPI()
tmdb = TMDb()
tmdb.api_key = config('TMDB_API')
ngrok.set_auth_token(config('NGROK_TOKEN'))
print(ngrok.connect('8000').public_url)
video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
base_directory = 'download-contents/'


class SearchModel(BaseModel):
    q: str


class DetailModel(BaseModel):
    id: int


@dataclass
class MovieModel:
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
        return MovieModel(
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


@dataclass
class MovieDetailModel:
    id: int
    link: str


@app.get("/popular-movies")
async def popular_movies():
    movie = Movie()
    popular = movie.popular()
    results = popular.get('results')
    movies = []
    for res in results:
        movies.append(MovieModel.from_json(res))
    return {"data": movies}


@app.get("/discover-movies")
async def discover_movies():
    movie = Movie()
    top_rated = movie.top_rated()
    results = top_rated.get('results')
    movies = []
    for res in results:
        movies.append(MovieModel.from_json(res))
    return {"data": movies}


@app.post("/search-movies")
async def search_endpoint(data: SearchModel):
    search_term = data.q
    search = Search()
    search_results = search.movies(search_term)
    results = search_results.get('results')
    movies = []
    for res in results:
        movies.append(MovieModel.from_json(res))
    return {"data": movies}


@app.post("/details")
async def details_endpoint(data: DetailModel):
    tmdb_id = data.id
    movie = Movie()
    details = movie.details(tmdb_id)

    ezflix = Ezflix(query=details['title'], media_type='movie', quality='720p', limit=1)
    movies = ezflix.search()
    return MovieDetailModel(tmdb_id, movies[0]['link'])


def long_running_task():
    global torrent_file
    torrent_file = TorrentDownloader("download.torrent", base_directory)
    torrent_file.start_download()


@app.post("/download")
async def download_endpoint(data: SearchModel):
    global future, currentLink
    link = data.q

    if currentLink != link:
        if future is not None:
            future.cancel()
        os.system("rm -rf download-contents")
        os.system("rm download.torrent")
        with open("download.torrent", "wb") as f:
            r = requests.get(link)
            f.write(r.content)
        os.mkdir('download-contents')
        future = executor.submit(long_running_task)
        while True:
            status = torrent_file._downloader.status()
            if status.progress > 0.03:
                break
    currentLink = link

    return json.dumps({"status": True})


@app.get("/stream")
async def stream_endpoint():
    def find_video_files(directory):
        video_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(root, file))
        return video_files

    fs = find_video_files(base_directory)
    if len(fs) > 0:
        video_path = fs[0]
    else:
        raise HTTPException(status_code=400)

    headers = {
        "Content-Disposition": f"attachment; filename={os.path.basename(video_path)}"}
    print(video_path)

    def read_video_file():
        with open(video_path, mode="rb") as video_file:
            while True:
                chunk = video_file.read(1024)  # You can adjust the chunk size as needed
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(read_video_file(), headers=headers, media_type="video/mp4")


if __name__ == "__main__":
    uvicorn.run(app)
