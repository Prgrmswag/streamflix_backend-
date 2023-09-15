import os
from pyngrok import ngrok
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
ngrok.set_auth_token(config('NGROK_TOKEN'))
print(ngrok.connect('8000').public_url)


class SearchModel(BaseModel):
    q: str


@app.get("/popular-movies")
async def popular_movies():
    movie = Movie()
    popular = movie.popular()
    print(popular)
    return popular


@app.post("/discover-movies")
async def discover_movies():
    movie = Movie()
    top_rated = movie.top_rated()
    print(top_rated)
    return top_rated


@app.post("/search-movies")
async def search_endpoint(data: SearchModel):
    search_term = data.q
    search = Search()
    search_results = search.movies(search_term)
    return search_results


@app.post("/details")
async def details_endpoint(data: SearchModel):
    tmdb_id = data.q
    movie = Movie()
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


@app.get('/')
async def test():
    return {'page': 1, 'results': [{'adult': False, 'backdrop_path': '/4XM8DUTQb3lhLemJC51Jx4a2EuA.jpg', 'genre_ids': [28, 80, 53], 'id': 385687, 'original_language': 'en', 'original_title': 'Fast X', 'overview': "Over many missions and against impossible odds, Dom Toretto and his family have outsmarted, out-nerved and outdriven every foe in their path. Now, they confront the most lethal opponent they've ever faced: A terrifying threat emerging from the shadows of the past who's fueled by blood revenge, and who is determined to shatter this family and destroy everything—and everyone—that Dom loves, forever.", 'popularity': 3870.68, 'poster_path': '/fiVW06jE7z9YnO4trhaMEdclSiC.jpg', 'release_date': '2023-05-17', 'title': 'Fast X', 'video': False, 'vote_average': 7.3, 'vote_count': 3668}, {'adult': False, 'backdrop_path': '/ctMserH8g2SeOAnCw5gFjdQF8mo.jpg', 'genre_ids': [35, 12, 14], 'id': 346698, 'original_language': 'en', 'original_title': 'Barbie', 'overview': 'Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.', 'popularity': 3173.706, 'poster_path': '/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg', 'release_date': '2023-07-19', 'title': 'Barbie', 'video': False, 'vote_average': 7.3, 'vote_count': 4348}, {'adult': False, 'backdrop_path': '/8pjWz2lt29KyVGoq1mXYu6Br7dE.jpg', 'genre_ids': [28, 878, 27], 'id': 615656, 'original_language': 'en', 'original_title': 'Meg 2: The Trench', 'overview': 'An exploratory dive into the deepest depths of the ocean of a daring research team spirals into chaos when a malevolent mining operation threatens their mission and forces them into a high-stakes battle for survival.', 'popularity': 2237.141, 'poster_path': '/4m1Au3YkjqsxF8iwQy0fPYSxE0h.jpg', 'release_date': '2023-08-02', 'title': 'Meg 2: The Trench', 'video': False, 'vote_average': 7, 'vote_count': 1701}, {'adult': False, 'backdrop_path': '/3tzPSJiCPqacAgRsMkMPof2ZinL.jpg', 'genre_ids': [27, 53], 'id': 1008042, 'original_language': 'en', 'original_title': 'Talk to Me', 'overview': 'When a group of friends discover how to conjure spirits using an embalmed hand, they become hooked on the new thrill, until one of them goes too far and unleashes terrifying supernatural forces.', 'popularity': 1918.428, 'poster_path': '/kdPMUMJzyYAc4roD52qavX0nLIC.jpg', 'release_date': '2023-07-26', 'title': 'Talk to Me', 'video': False, 'vote_average': 7.2, 'vote_count': 422}, {'adult': False, 'backdrop_path': '/53z2fXEKfnNg2uSOPss2unPBGX1.jpg', 'genre_ids': [27, 9648, 53], 'id': 968051, 'original_language': 'en', 'original_title': 'The Nun II', 'overview': 'In 1956 France, a priest is violently murdered, and Sister Irene begins to investigate. She once again comes face-to-face with a powerful evil.', 'popularity': 1601.054, 'poster_path': '/5gzzkR7y3hnY8AD1wXjCnVlHba5.jpg', 'release_date': '2023-09-06', 'title': 'The Nun II', 'video': False, 'vote_average': 6.7, 'vote_count': 148}, {'adult': False, 'backdrop_path': '/yF1eOkaYvwiORauRCPWznV9xVvi.jpg', 'genre_ids': [28, 12, 878], 'id': 298618, 'original_language': 'en', 'original_title': 'The Flash', 'overview': "When his attempt to save his family inadvertently alters the future, Barry Allen becomes trapped in a reality in which General Zod has returned and there are no Super Heroes to turn to. In order to save the world that he is in and return to the future that he knows, Barry's only hope is to race for his life. But will making the ultimate sacrifice be enough to reset the universe?", 'popularity': 1224.607, 'poster_path': '/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg', 'release_date': '2023-06-13', 'title': 'The Flash', 'video': False, 'vote_average': 6.9, 'vote_count': 2816}, {'adult': False, 'backdrop_path': '/4fLZUr1e65hKPPVw0R3PmKFKxj1.jpg', 'genre_ids': [16, 35, 10751, 14, 10749], 'id': 976573, 'original_language': 'en', 'original_title': 'Elemental', 'overview': 'In a city where fire, water, land and air residents live together, a fiery young woman and a go-with-the-flow guy will discover something elemental: how much they have in common.', 'popularity': 1169.434, 'poster_path': '/6oH378KUfCEitzJkm07r97L0RsZ.jpg', 'release_date': '2023-06-14', 'title': 'Elemental', 'video': False, 'vote_average': 7.8, 'vote_count': 1969}, {'adult': False, 'backdrop_path': '/9m161GawbY3cWxe6txd1NOHTjd0.jpg', 'genre_ids': [878, 12, 28, 14], 'id': 335977, 'original_language': 'en', 'original_title': 'Indiana Jones and the Dial of Destiny', 'overview': "Finding himself in a new era, and approaching retirement, Indy wrestles with fitting into a world that seems to have outgrown him. But as the tentacles of an all-too-familiar evil return in the form of an old rival, Indy must don his hat and pick up his whip once more to make sure an ancient and powerful artifact doesn't fall into the wrong hands.", 'popularity': 1134.897, 'poster_path': '/Af4bXE63pVsb2FtbW8uYIyPBadD.jpg', 'release_date': '2023-06-28', 'title': 'Indiana Jones and the Dial of Destiny', 'video': False, 'vote_average': 6.7, 'vote_count': 1567}, {'adult': False, 'backdrop_path': '/c6Splshb8lb2Q9OvUfhpqXl7uP0.jpg', 'genre_ids': [28, 53], 'id': 717930, 'original_language': 'en', 'original_title': 'Kandahar', 'overview': 'After his mission is exposed, an undercover CIA operative stuck deep in hostile territory in Afghanistan must fight his way out, alongside his Afghan translator, to an extraction point in Kandahar, all whilst avoiding elite enemy forces and foreign spies tasked with hunting them down.', 'popularity': 837.193, 'poster_path': '/lCanGgsqF4xD2WA5NF8PWeT3IXd.jpg', 'release_date': '2023-05-25', 'title': 'Kandahar', 'video': False, 'vote_average': 6.7, 'vote_count': 444}, {'adult': False, 'backdrop_path': '/2ii07lSwHarg0gWnJoCYL3Gyd1j.jpg', 'genre_ids': [35, 12], 'id': 912908, 'original_language': 'en', 'original_title': 'Strays', 'overview': 'When Reggie is abandoned on the mean city streets by his lowlife owner, Doug, Reggie is certain that his beloved owner would never leave him on purpose. But once Reggie falls in with Bug, a fast-talking, foul-mouthed stray who loves his freedom and believes that owners are for suckers, Reggie finally realizes he was in a toxic relationship and begins to see Doug for the heartless sleazeball that he is.', 'popularity': 789.786, 'poster_path': '/n1hqbSCtyBAxaXEl1Dj3ipXJAJG.jpg', 'release_date': '2023-08-17', 'title': 'Strays', 'video': False, 'vote_average': 7.4, 'vote_count': 250}, {'adult': False, 'backdrop_path': '/waBWlJlMpyFb7STkFHfFvJKgwww.jpg', 'genre_ids': [28, 18], 'id': 678512, 'original_language': 'en', 'original_title': 'Sound of Freedom', 'overview': 'The story of Tim Ballard, a former US government agent, who quits his job in order to devote his life to rescuing children from global sex traffickers.', 'popularity': 778.63, 'poster_path': '/kSf9svfL2WrKeuK8W08xeR5lTn8.jpg', 'release_date': '2023-07-03', 'title': 'Sound of Freedom', 'video': False, 'vote_average': 8, 'vote_count': 443}, {'adult': False, 'backdrop_path': '/2vFuG6bWGyQUzYS9d69E5l85nIz.jpg', 'genre_ids': [28, 12, 878], 'id': 667538, 'original_language': 'en', 'original_title': 'Transformers: Rise of the Beasts', 'overview': 'When a new threat capable of destroying the entire planet emerges, Optimus Prime and the Autobots must team up with a powerful faction known as the Maximals. With the fate of humanity hanging in the balance, humans Noah and Elena will do whatever it takes to help the Transformers as they engage in the ultimate battle to save Earth.', 'popularity': 751.531, 'poster_path': '/gPbM0MK8CP8A174rmUwGsADNYKD.jpg', 'release_date': '2023-06-06', 'title': 'Transformers: Rise of the Beasts', 'video': False, 'vote_average': 7.5, 'vote_count': 3143}, {'adult': False, 'backdrop_path': '/rV56FkcHkzHJcBOOqoCeSDnoBff.jpg', 'genre_ids': [28, 18], 'id': 990140, 'original_language': 'cn', 'original_title': '天龍八部之喬峰傳', 'overview': 'Qiao Feng is the respected leader of a roving band of martial artists. After he is wrongfully accused of murder and subsequently exiled, Qiao Feng goes on the run in search of answers about his own mysterious origin story—and the unknown enemies working to destroy him from the shadows.', 'popularity': 749.463, 'poster_path': '/jGKCpt3zzbGZbgoza6HCvecqElM.jpg', 'release_date': '2023-01-16', 'title': 'Sakra', 'video': False, 'vote_average': 6.4, 'vote_count': 76}, {'adult': False, 'backdrop_path': '/w2nFc2Rsm93PDkvjY4LTn17ePO0.jpg', 'genre_ids': [16, 35, 28], 'id': 614930, 'original_language': 'en', 'original_title': 'Teenage Mutant Ninja Turtles: Mutant Mayhem', 'overview': "After years of being sheltered from the human world, the Turtle brothers set out to win the hearts of New Yorkers and be accepted as normal teenagers through heroic acts. Their new friend April O'Neil helps them take on a mysterious crime syndicate, but they soon get in over their heads when an army of mutants is unleashed upon them.", 'popularity': 729.356, 'poster_path': '/ueO9MYIOHO7M1PiMUeX74uf8fB9.jpg', 'release_date': '2023-07-31', 'title': 'Teenage Mutant Ninja Turtles: Mutant Mayhem', 'video': False, 'vote_average': 7.2, 'vote_count': 435}, {'adult': False, 'backdrop_path': '/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg', 'genre_ids': [16, 28, 12], 'id': 569094, 'original_language': 'en', 'original_title': 'Spider-Man: Across the Spider-Verse', 'overview': 'After reuniting with Gwen Stacy, Brooklyn’s full-time, friendly neighborhood Spider-Man is catapulted across the Multiverse, where he encounters the Spider Society, a team of Spider-People charged with protecting the Multiverse’s very existence. But when the heroes clash on how to handle a new threat, Miles finds himself pitted against the other Spiders and must set out on his own to save those he loves most.', 'popularity': 669.326, 'poster_path': '/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg', 'release_date': '2023-05-31', 'title': 'Spider-Man: Across the Spider-Verse', 'video': False, 'vote_average': 8.5, 'vote_count': 4175}, {'adult': False, 'backdrop_path': '/fgsHxz21B27hOOqQBiw9L6yWcM7.jpg', 'genre_ids': [27, 9648, 53], 'id': 439079, 'original_language': 'en', 'original_title': 'The Nun', 'overview': 'A priest with a haunted past and a novice on the threshold of her final vows are sent by the Vatican to investigate the death of a young nun in Romania and confront a malevolent force in the form of a demonic nun.', 'popularity': 612.272, 'poster_path': '/sFC1ElvoKGdHJIWRpNB3xWJ9lJA.jpg', 'release_date': '2018-09-05', 'title': 'The Nun', 'video': False, 'vote_average': 5.9, 'vote_count': 5973}, {'adult': False, 'backdrop_path': '/2QL5j6mB4ZpyBcVr0WO9H9MQGBu.jpg', 'genre_ids': [28, 12, 18, 14, 36], 'id': 734253, 'original_language': 'hi', 'original_title': 'आदिपुरुष', 'overview': "7000 years ago, Ayodhya's Prince Raghava and Prince Sesh along with the Mighty Vanar Warriors travels to the island of Lanka with an aim to rescue Raghava's wife Janaki, who has been abducted by Lankesh, the king of Lanka.", 'popularity': 609.397, 'poster_path': '/1H2xEZOixs0z0JKwyjANZiKNNVJ.jpg', 'release_date': '2023-06-16', 'title': 'Adipurush', 'video': False, 'vote_average': 5.1, 'vote_count': 36}, {'adult': False, 'backdrop_path': '/jkKVLzLWjSvTnc84VzeljhSy6j8.jpg', 'genre_ids': [10749, 18], 'id': 820525, 'original_language': 'en', 'original_title': 'After Everything', 'overview': 'Besieged by writer’s block and the crushing breakup with Tessa, Hardin travels to Portugal in search of a woman he wronged in the past – and to find himself. Hoping to win back Tessa, he realizes he needs to change his ways before he can make the ultimate commitment.', 'popularity': 585.117, 'poster_path': '/gZLGCibvFY4zmt8sWUZcbBTHRtk.jpg', 'release_date': '2023-09-13', 'title': 'After Everything', 'video': False, 'vote_average': 6, 'vote_count': 4}, {'adult': False, 'backdrop_path': '/vMJb1D40wQNbTveNVFpNbo12faA.jpg', 'genre_ids': [28, 36], 'id': 1049951, 'original_language': 'en', 'original_title': 'Viking: Bloodlust', 'overview': 'A band of vikings are on the run from a blood thirsty group of Berserkers who want to fight to the death.', 'popularity': 569.706, 'poster_path': '/xveBJmViwHdgjH3UQQmImkHOW7B.jpg', 'release_date': '2023-04-21', 'title': 'Viking: Bloodlust', 'video': False, 'vote_average': 7.2, 'vote_count': 20}, {'adult': False, 'backdrop_path': '/2zzaJ9jzyK1Am8XoS0dFjmP8V0L.jpg', 'genre_ids': [28, 53, 27], 'id': 1135229, 'original_language': 'en', 'original_title': 'I Am Rage', 'overview': 'An ancient cult embroiled in a sinister blood trade makes the deadly mistake of abducting a young woman with a violent, shocking past.', 'popularity': 554.051, 'poster_path': '/iclmQs4O5dy7EAkbykI1qkowfK2.jpg', 'release_date': '2023-09-14', 'title': 'I Am Rage', 'video': False, 'vote_average': 6.3, 'vote_count': 4}], 'total_pages': 40069, 'total_results': 801369}


if __name__ == "__main__":
    uvicorn.run(app)
