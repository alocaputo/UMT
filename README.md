# UMT
Universal Media Tracker

---
## movTra

movTra is a self hosted movie tracking software written in python using django and [The Movie Database](https://www.themoviedb.org/) API.

## Installation:
#### Requirements:
* TMDb API key
* Python3
* Django

Enter your TMDBb API key and the Django's secret key in `UMT/.env`
Such as:
```
APIKEY='yourAPIKEY'
SECRET_KEY='yourSECRET_KEY'
```
Then:
```
python ./manage.py makemigrations
python ./manage.py migrate
```
And finally run the server:
```
python ./manage.py runserver
```

### Features:
* **Diary**: Log a movie with your rating, review of it, and date in which you have seen it.
* **Lists**: Create lists of movies.
* **Upcoming**: Displays the upcoming movies.
* **Now Playing**: Displays the movies now in theatres.
* **Stats**: Display stats of your viewings.

### TODO:
* Watchlist
* Import/Export

--
## tvTra
--
## bookTra
--
## gameTra
