from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Movie, List, isIn, Genres, isGenre, WorkedAsCast, WorkedAsCrew, Company, Produce, Country, ProductionCountry, Language, SpokenLanguage, LogEntry
from .utils import tmdb_api_wrap
import pprint
import csv
import codecs
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core import serializers
import json
# Create your views here.

def index(request):
    latest_movies_list = Movie.objects.raw("""  select movtra_movie.*, movtra_logentry.* 
                                                from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id 
                                                where movtra_logentry.date is not null 
                                                order by date desc;
                                            """)
    context = {'latest_movies_list': latest_movies_list, 'all': False}
    return render(request, 'movtra/index.html', context)

def all(request):
    latest_movies_list = Movie.objects.order_by('-last_updated')[:20]
    context = {'latest_movies_list': latest_movies_list, 'all': True}
    return render(request, 'movtra/index.html', context)

def upcoming(request):
    upcoming = tmdb_api_wrap.getUpcoming()
    context =  {'results': upcoming,
                 'type': 0 #it's not a search
                }
    return render(request, 'movtra/results.html', context)

def nowplaying(request):
    nowplaying = tmdb_api_wrap.getNowPlaying()
    context = {'results': nowplaying,
                'type': 0 #it's not a search
                }
    return render(request, 'movtra/results.html', context)

# Return the serialization of a Movie entry
def serialize_movie(movie_entry):
    movie = {}
    for attr,k in movie_entry.__dict__.items():
        movie[attr] = k
    return movie

# Movie detail view
def detail(request, tmdbID):
        local = False # db presence flag
        try:
            # Check if the movie is in the db
            movie = Movie.objects.get(id=tmdbID)
            movie_serialized = serialize_movie(movie)
            local = True
        except Movie.DoesNotExist:
            movie = None
        if movie is None: # If not present in the db, get the information
            movie = tmdb_api_wrap.getMovieByID(tmdbID)
            genres=movie['genres']
            directors = {}
            dID=0
            for p in movie['credits']['crew']:
               if p['job'] == 'Director':
                    pprint.pprint(p)
                    directors[dID] = {'name': p['name'], 'id': p['id']}
                    dID+=1
    
            g = []
            for gen in genres:
                g.append(gen['name'])
            return render(request, 'movtra/detail.html', {'movie': movie, 'genres': genres, 'directors': directors, 'local': local})
        else: # Otherwise look if it's present in any list
            isin = isIn.objects.filter(movie=movie).order_by('list')
            lists = {}
            lID=0
            for l in isin:
                lists[lID] = {'id': l.list.id,
                          'name': l.list.name}
                lID+=1

            # Uniform the genres and directors
            isgenre = isGenre.objects.filter(movie=movie)
            genres = []
            for g in isgenre:
                genres.append(g.genre.name)
            mov = tmdb_api_wrap.getMovieByID(tmdbID)
            genres=mov['genres']
            
            directors = {}
            dID=0
            for p in mov['credits']['crew']:
               if p['job'] == 'Director':
                    pprint.pprint(p)
                    directors[dID] = {'name': p['name'], 'id': p['id']}
                    dID+=1

            # Get diary entries
            diary_entries = LogEntry.objects.filter(movie=movie)
            diary = {}
            eID = 0
            for e in diary_entries:
                diary[eID] = {'id': e.id,
                              'date': e.date,
                              'rating': e.rating,
                              'review': e.review}
                eID+=1
            return render(request, 'movtra/detail.html', {'movie': movie, 'lists': lists, 'genres': genres, 'directors' : directors, 'diary': diary, 'local': local})

# Log Movie function (refactor)
def logMovie(request):
    if request.method == 'POST':	
        date = request.POST.get('bday')
        tmdbID = request.POST.get('tmdbID')
        rating = request.POST.get('rating')
        review = ""
        review = request.POST.get('review')
        data = {'tmdbID': tmdbID , 'date': date, 'rating': rating, 'review': review}
        
        try:
            mov = Movie.objects.get(id=tmdbID)
        except Movie.DoesNotExist:
            mov = None
        if mov is None:
            addMovie(tmdbID)
        LogEntry.addLogEntry(data)
    return redirect(request.META['HTTP_REFERER'])


#TODO: add next page
def results(request, query, page):
    pprint.pprint(request.POST)
    if page != '':
        page = page
    else:
        page = 1
    if request.method == 'POST':
            movieName = request.POST.get('searchTitle')
            if movieName == '':
                movieName = query
    else:
        movieName = query
    query = movieName

    if ' ' in movieName:
        movieName = movieName.replace(' ','+')
    results = tmdb_api_wrap.getMovieByName(movieName,page)
    total_pages = results[1]

    if page == total_pages:
        isNext = False
    else:
        isNext = True
    
    if page == 1:
        isBack = False
    else:
        isBack = True
    context = {'query': movieName ,'next_page': int(page)+1, 'isNext': isNext, 'back_page': int(page)-1 ,'isBack': isBack, 'page': page, 'results': results[0] , 'total_pages': total_pages, 'type': 0}
    return render(request, 'movtra/results.html', context)



# General purpose function to add a movie given its id to the dB
def addMovie(tmdbID):
    try:
        Movie.objects.get(pk=tmdbID)
    except Movie.DoesNotExist:
        movie = tmdb_api_wrap.getMovieByID(tmdbID)
        try:
            mov = Movie.addShow(movie)
            for genre in movie['genres']:
                try:
                    genreID = Genres.objects.get(pk=genre['id'])
                    genreID = genre['id']
                except Genres.DoesNotExist:
                    genreID = Genres.addGenre(genre)
                    isGenre.addGenreToMovie(tmdbID,genreID)
            for company in movie['production_companies']:
                try:
                    companyID = Company.objects.get(pk=company['id'])
                    companyID = company['id']
                except Company.DoesNotExist:
                    companyID = Company.addNewCompany(company)
                    Produce.addProdutionCompany(tmdbID, companyID)

            for country in movie['production_countries']:
                try:
                    countryID = Country.objects.get(pk=country['iso_3166_1'])
                    countryID = country['iso_3166_1']
                except Country.DoesNotExist:
                    countryID = Country.addCountry(country)
                    ProductionCountry.addProductionCountry(tmdbID, countryID)
            for language in movie['spoken_languages']:
                try:
                    languageID = Language.objects.get(pk=language['iso_639_1'])
                    languageID = language['iso_639_1']
                except Language.DoesNotExist:
                    languageID = Language.addLanguage(language)
                    SpokenLanguage.addSpokenLanguage(tmdbID, languageID)
            # cast & crew
            credits = movie['credits']
            for personData in credits['cast']:
                try:
                    WorkedAsCast.objects.get(movie = mov, 
                                        personID = personData['id'], 
                                        character = personData['character'],
                                        order = personData['order'])
                except WorkedAsCast.DoesNotExist:
                    WorkedAsCast.addPersonToCast(personData, tmdbID)
            for personData in credits['crew']:
                try:
                    WorkedAsCrew.objects.get(movie = mov, 
                                        personID = personData['id'], 
                                        credit_id = personData['credit_id'],
		                                department = personData['department'],
		                                job = personData['job'])
                except WorkedAsCrew.DoesNotExist:
                    WorkedAsCrew.addPersonToCrew(personData, tmdbID)      
                      
        except Exception as e:
            print("orco can")
            print(e)
            isGenre.objects.filter(movie=tmdbID).delete()
            Produce.objects.filter(movie=tmdbID).delete()
            WorkedAsCast.objects.filter(movie=tmdbID).delete()
            WorkedAsCrew.objects.filter(movie=tmdbID).delete()
            Movie.objects.filter(id=tmdbID).delete()

# Update information for existing movies
def updateData(request, tmdbID):
    if request.method == 'POST':
        try:
            mov = Movie.objects.get(id=tmdbID)
        except IntegrityError:
            print('Movie not present in the db')
        movie = tmdb_api_wrap.getMovieByID(tmdbID)
        Movie.addShow(movie)
        for genre in movie['genres']:
            try:
                genreID = Genres.objects.get(pk=genre['id'])
                genreID = genre['id']
            except Genres.DoesNotExist:
                genreID = Genres.addGenre(genre)
                isGenre.addGenreToMovie(tmdbID,genreID)
        for company in movie['production_companies']:
            try:
                companyID = Company.objects.get(pk=company['id'])
                companyID = company['id']
            except Company.DoesNotExist:
                companyID = Company.addNewCompany(company)
                Produce.addProdutionCompany(tmdbID, companyID)
        for country in movie['production_countries']:
            try:
                countryID = Country.objects.get(pk=country['iso_3166_1'])
                countryID = country['iso_3166_1']
            except Country.DoesNotExist:
                countryID = Country.addCountry(country)
                ProductionCountry.addProductionCountry(tmdbID, countryID)
        for language in movie['spoken_languages']:
            try:
                languageID = Language.objects.get(pk=language['iso_639_1'])
                languageID = language['iso_639_1']
            except Language.DoesNotExist:
                languageID = Language.addLanguage(language)
                SpokenLanguage.addSpokenLanguage(tmdbID, languageID)
        # cast & crew
        credits = movie['credits']
        for personData in credits['cast']:
            try:
                WorkedAsCast.objects.get(movie = mov, 
                                        personID = personData['id'], 
                                        character = personData['character'],
                                        order = personData['order'])
            except WorkedAsCast.DoesNotExist:
                WorkedAsCast.addPersonToCast(personData, tmdbID)
        for personData in credits['crew']:
            try:
                WorkedAsCrew.objects.get(movie = mov, 
                                    personID = personData['id'], 
                                    credit_id = personData['credit_id'],
                                    department = personData['department'],
                                    job = personData['job'])
            except WorkedAsCrew.DoesNotExist:
                WorkedAsCrew.addPersonToCrew(personData, tmdbID)        
        return HttpResponseRedirect('/movie/%d' % tmdbID)
    return HttpResponseRedirect('/')

#List view (lists)
def lists(request):
    context = {}
    list = List.objects.all()
    context['list'] = list
    return render(request, 'movtra/lists.html', context)

#List view (list of movies)
def listDetail(request, id):
    listID = List.objects.get(id=id)

    movies = isIn.objects.filter(list=listID).order_by('id')
    if not movies.exists:
        watched_count = 0
    else:
        watched_count = Movie.objects.raw('select distinct movtra_movie.* , movtra_logentry.id as log_id from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id=' + str(id) + ' group by movtra_movie.id;')
        w=0
        for wc in watched_count:
            w+=1

    print(watched_count)
    context = {'movies': movies, 'list': listID ,'total':len(movies), 'watched': len(list(watched_count)), 'logentry': list(watched_count)}
    return render(request, 'movtra/listDetail.html', context)

#Import button in list (WIP)
def importList(request, id):
    """movies = tmdb_api_wrap.importImdb('./movtra/utils/10.csv')
    i=0
    for movie in movies:
        tmdbID = tmdb_api_wrap.getMovieByImdbID(movie)['id']
        addMovie(tmdbID)
        i=i+1
        try:
            isIn.addShow(tmdbID,id)
        except IntegrityError:
            print(str(i) + ': ' + str(tmdbID) + ' duplicate')
        print(str(i) + ': ' + str(tmdbID) + ' added')
    return HttpResponseRedirect('../')"""
    letterboxdImport("/home/theloca95/letterbox/diary.csv")
    return HttpResponseRedirect('../')

#Imports movies from a letterboxd file
def letterboxdImport(file):
    ids = []
    firstline = True
    i = 1
    with codecs.open(file, "r", encoding='utf-8', errors='ignore') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if firstline:
                firstline = False
                continue
            #res.append(row[1])
            #movie = getMovieByImdbID(row[1])
            #res.append(movie)
            title = row[1]
            year = row[2]
            date = row[-1]
            rating=row[4]
            movie = tmdb_api_wrap.searchByYear(title,year)[0]
            print("{}: {}".format(i,movie['id']))
            addMovie(movie['id'])
            data = {'tmdbID': movie['id'], 'date': date , 'rating': rating, 'review': ''}
            LogEntry.addLogEntry(data)
            i=i+1
    return ids

#Create a new list
def newList(request):
    context = {}
    if request.method == 'POST':
        listTitle = request.POST.get('listTitle')
        print(listTitle)
        list = List.objects.all()
        print(list)
        List.addShow(listTitle)

    context['list'] = list
    return render(request, 'movtra/lists.html', context)

def addToList(request, id):
    context = {}
    movieName = request.POST.get('listTitle')
    if ' ' in movieName:
        movieName = movieName.replace(' ','+')
    results = tmdb_api_wrap.getMovieByName(movieName,1) #return (results, number of results)
    context = {'results': results[0] , 'total_pages': results[1], 'list_id': id, 'type': 1} # type 1 list
    return render(request, 'movtra/results.html', context)

def addMovieToList(request, id):
    context = {}
    if request.method == 'POST':
        listID = int(request.POST.get('listid'))
        addMovie(id)
        try:
            isIn.addShow(id,listID)
        except IntegrityError:
            print('duplicate')
        return HttpResponseRedirect('/lists/%d' % listID)
    return HttpResponseRedirect('/')

def editList(request, id):
    listID = List.objects.get(id=id)

    movies = isIn.objects.filter(list=listID).order_by('id')
    movs = {}
    movieIDs = []
    wmovieIDs = []
    i=0
    for m in movies:
        #movieIDs.append(m.movie.id)
        movs[i] = {'id': m.movie.id, 'title': m.movie.title, 'year': str(m.movie.release_date)[:4]}
        i+=1

    if not movies.exists:
        #watched_count = len(isIn.objects.filter(list=list).filter(movie__status_watched=True))
        watched_count = 0
    else:
        #watched_count = Movie.objects.raw('select distinct movtra_movie.* from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id='+str(id) +';')
        watched_count = Movie.objects.raw('select distinct movtra_movie.* , movtra_logentry.id as log_id from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id=' + str(id) + ' group by movtra_movie.id;')
        #watched_count = Movie.objects.raw('select movtra_movie.*, movtra_logentry.date from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id order by date desc;')
        w=0
        for wc in watched_count:
            wmovieIDs.append(wc.id)
            w+=1

    #print(watched_count)
    #context = {'movies': movieIDs, 'list': id ,'total':len(movieIDs), 'watched': w, 'logentry': list(watched_count)}
    context = {'movies': movs, 'list': id ,'total':i, 'watched': w, 'logentry': wmovieIDs}
    return render(request, 'movtra/editList.html', context)
    #return JsonResponse(context)
    #return HttpResponse(json.dumps(context))

def editLists(request):
    context = {}
    list = List.objects.all()
    context['list'] = list
    return render(request, 'movtra/listsEdit.html', context)

#deprecated I think
def editListsAjax(request):
    context = {}
    list = List.objects.all()
    data = serializers.serialize('json', List.objects.all(), fields=('id',))
    context['list'] = data
    #return render(request, 'movtra/listsEdit.html', context)
    return JsonResponse(context)

#deprecated
def removeList(request, id):
    if request.method == 'POST':
        print('post')
        list_id = int(request.POST.get('listid'))
        List.objects.filter(id=list_id).delete()
        print('deleted')
        print(list_id)
    isIn.objects.filter(list_id=id).delete()
    List.objects.filter(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def removeListsGET(request):
    if request.method == 'GET':
        listID = request.GET['list_id']
        List.objects.filter(id=listID).delete()
        isIn.objects.filter(list_id=listID).delete()
        return HttpResponse("Success!")
    else:
        print("nope")
        return HttpResponse("Request method is not a GET")

#deprecated
def removeMovieFromList(request, id, tmdbID):
    if request.method == 'POST':
        print(id)
        print(tmdbID)
        print(isIn.objects.filter(list_id=id).filter(movie_id=tmdbID))
        isIn.objects.filter(list_id=id).filter(movie_id=tmdbID).delete()

    isIn.objects.filter(list_id=id).filter(movie_id=tmdbID).delete()
    return redirect(request.META['HTTP_REFERER'])

def removeMovieFromListGET(request):
    if request.method == 'GET':
        movieID = request.GET['movie_id']
        listID = request.GET['list_id']
        isIn.objects.filter(list_id=listID).filter(movie_id=movieID).delete()
        return HttpResponse("Success!")
    else:
        print("nope")
        return HttpResponse("Request method is not a GET")

def removeDiaryEntry(request, tmdbID, diaryID):
    LogEntry.objects.filter(id=diaryID).delete()
    return redirect(request.META['HTTP_REFERER'])

#TODO
def editReview(request, tmdbID):
    movie = get_object_or_404(Movie, pk=tmdbID)
    context = {'movie': movie}
    if request.method == 'POST':
        print(request.POST.get('text'))
    return render(request, 'movtra/editReview.html', context)

def saveReview(request, tmdbID):
    if request.method == 'POST':
        data = request.POST.get('text')
    movie = get_object_or_404(Movie, pk=tmdbID)
    Movie.addReview(movie,data)
    return HttpResponseRedirect('./')

def personDetail(request, tmdbID):
    personData = tmdb_api_wrap.getPersonByID(tmdbID)
    filmography = tmdb_api_wrap.getFilmography(tmdbID)
    
    
    raw_watched = Movie.objects.raw("""select distinct movtra_movie.id
                                    from  movtra_workedascrew, movtra_movie
                                    where  movtra_workedascrew.personID="""+str(tmdbID)+""" and movtra_movie.id=movtra_workedascrew.movie_id""")
    watched = []
    for w in raw_watched:
        watched.append(int(w.id))
    # horrible way to get sorted filmography
    s = {}
    for j, q in filmography['crew'].items():       
        res = {}
        for k, v in q.items():
            res[v['id']] = v['release_date']
        rd = sorted(res.values())
        m = 0
        y=0

        # put blanks at the end of the array
        while y<len(rd) and rd[m] == '':
            n = 0
            while n<len(rd)-1:
                rd[n] = rd[n+1]
                n +=1
            rd[len(rd)-1] = ''
            y +=1

        ps = {}

        for k, v in q.items():
            i = rd.index(v['release_date'])
            ps[i] = v
        sps = dict(sorted(ps.items()))
        s[j] = sps

    
    crew_slug = {k.replace(' ', '_'): v for k, v in s.items()}
    context = {'person': personData, 'cast': filmography['cast'], 'crew': filmography['crew'], 'crew_slug': crew_slug, 'watched':watched}
    return render(request, 'movtra/personDetail.html', context)

#TODO cache manager
# if (\wsdasd.jpg) exists use it else download and use it
# genres page

#select movtra_movie.id
#from movtra_isgenre, movtra_movie
#where movtra_isgenre.genre_id=18 and movtra_isgenre.movie_id=movtra_movie.id;

#log movie when adding

#https://stackoverflow.com/questions/34774138/reload-table-data-in-django-without-refreshing-the-page/34775420
