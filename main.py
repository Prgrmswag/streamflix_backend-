# swaraj 

import json
import os
import time
from dataclasses import dataclass

import requests
import uvicorn
from decouple import config
from ezflix import Ezflix
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok
from fastapi.responses import FileResponse
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


@app.post("/details")
async def details_endpoint(data: DetailModel):
    try:
        tmdb_id = data.id
        movie = Movie()
        details = movie.details(tmdb_id)

        ezflix = Ezflix(query=details['title'], media_type='movie', quality='720p', limit=1)
        movies = ezflix.search()
        if movies:
            return MovieDetailModel(tmdb_id, movies[0]['link'])
        else:
            raise HTTPException(status_code=404, detail="No torrent found for this movie")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def long_running_task():
    global torrent_file
    try:
        print("Starting long running task for torrent download.")
        torrent_file = TorrentDownloader("download.torrent", base_directory)
        torrent_file.start_download()
    except Exception as e:
        print(f"Error in long_running_task: {e}")
        raise


@app.post("/download")
async def download_endpoint(data: SearchModel):
    global future, currentLink, torrent_file
    try:
        link = data.q

        if currentLink != link:
            if future is not None:
                print("Cancelling previous download task.")
                future.cancel()

            # Ensure old content is removed
            if os.path.exists("download-contents"):
                print("Removing old download-contents directory.")
                os.system("rm -rf download-contents")
            if os.path.exists("download.torrent"):
                print("Removing old download.torrent file.")
                os.remove("download.torrent")

            # Download the new torrent file
            print(f"Downloading torrent file from link: {link}")
            with open("download.torrent", "wb") as f:
                r = requests.get(link)
                f.write(r.content)

            # Prepare the directory for downloads
            print("Creating new download-contents directory.")
            os.mkdir('download-contents')

            # Start the download task
            future = executor.submit(long_running_task)

            # Wait for download to finish
            while True:
                if torrent_file is None:
                    raise HTTPException(status_code=500, detail="TorrentDownloader not initialized")
                status = torrent_file._downloader.status()
                print(f"Download status: {status.progress}")
                if status.progress >= 1:
                    print("Download complete.")
                    break
                time.sleep(5)  # Pause briefly to reduce load

        currentLink = link
        return json.dumps({"status": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stream")
async def stream_endpoint():
    try:
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
            raise HTTPException(status_code=400, detail="No video files found")

        headers = {
            "Content-Disposition": f"attachment; filename={os.path.basename(video_path)}"}
        print(f"Streaming video: {video_path}")

        return FileResponse(video_path, headers=headers, media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app)
