from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Movie, List, isIn, Genres, isGenre, Person, WorkedAsCast, WorkedAsCrew, Company, Produce, Country, ProductionCountry, Language, SpokenLanguage, LogEntry
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
	text = request.POST.get('movieName')
	if(text != None):
		movie = tmdb_api_wrap.getMovieByID(text)
		Movie.addShow(movie)
		print(text)
	#WHY?????????????????????????????????????!!!!!!!!!!!!!!!!!!
	latest_movies_list = Movie.objects.raw('select movtra_movie.*, movtra_logentry.* from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id where movtra_logentry.date is not null order by date desc;')
	context = {'latest_movies_list': latest_movies_list, 'all':False}
	return render(request, 'movtra/index.html', context)

def all(request):
	text = request.POST.get('movieName')
	if(text != None):
		movie = tmdb_api_wrap.getMovieByID(text)
		Movie.addShow(movie)
		print(text)
	latest_movies_list = Movie.objects.order_by('-last_updated')[:20]
	context = {'latest_movies_list': latest_movies_list, 'all':True}
	return render(request, 'movtra/index.html', context)

def upcoming(request):
	upcoming = tmdb_api_wrap.getUpcoming()
	context = {'results': upcoming, 'search': False}
	return render(request, 'movtra/results.html', context)

def nowplaying(request):
	nowplaying = tmdb_api_wrap.getNowPlaying()
	context = {'results': nowplaying, 'search': False}
	return render(request, 'movtra/results.html', context)

def detail(request, tmdbID):
	try:
		movie = Movie.objects.get(id=tmdbID)
	except Movie.DoesNotExist:
		movie = None	
	if movie is None:
		movie = get_object_or_404(Movie, pk=tmdbID)
		return render(request, 'movtra/detail.html', {'movie': movie})
	else:
		isin = isIn.objects.filter(movie=movie).order_by('list')
		isgenre = isGenre.objects.filter(movie=movie)
		crew = WorkedAsCrew.objects.filter(movie=movie,job="Director")
		diary = LogEntry.objects.filter(movie=movie)
		return render(request, 'movtra/detail.html', {'movie': movie, 'isIn': isin, 'isGenre': isgenre, 'crew' : crew, 'diary': diary})

def seen(request):
	if request.method == 'POST':
		tmdbID = request.POST.get('seen')
		movie = get_object_or_404(Movie, pk=tmdbID)
		if movie:
			movie.toggleWst()
	return redirect(request.META['HTTP_REFERER'])

def rating(request):
	if request.method == 'POST':
		date = request.POST.get('bday')
		tmdbID = request.POST.get('tmdbID')
		rating = request.POST.get('rating')
		review = ""
		review = request.POST.get('review')
		data = {'tmdbID': tmdbID , 'date': date, 'rating': rating, 'review': review}
		LogEntry.addLogEntry(data)
	return redirect(request.META['HTTP_REFERER'])


def results(request):
	movieName = request.POST.get('searchTitle')
	if ' ' in movieName:
		movieName = movieName.replace(' ','+')
	results = tmdb_api_wrap.getMovieByName(movieName)
	context = {'results': results , 'search': True}
	return render(request, 'movtra/results.html', context)

def resDetail(request, tmdbID):
	movie = tmdb_api_wrap.getMovieByID(tmdbID)
	genres=movie['genres']
	pprint.pprint(genres)
	g = []
	for gen in genres:
		g.append(gen['name'])
	try:
		mov = Movie.objects.get(id=movie['id'])
	except Movie.DoesNotExist:
		mov = None	
	if mov is None:
		return render(request, 'movtra/resDetail.html', {'movie': movie, 'genres': g })
	else:
		return render(request, 'movtra/detail.html', {'movie': mov, 'genres': g})
	

def add(request):
	isSeen = False
	
	if request.method == 'POST':
		seen = request.POST.get('add')
		tmdbID = request.POST.get('tmdbID')
		print("Movie ID")
		print(tmdbID)
		addMovie(tmdbID)

	return HttpResponseRedirect('/movie/'+tmdbID )

def addMovie(tmdbID):
	try:
		Movie.objects.get(pk=tmdbID)
	except Movie.DoesNotExist:	
		movie = tmdb_api_wrap.getMovieByID(tmdbID)
		try:
			mov = Movie.addShow(movie)
			new = 0
			old = 0
			print('genres: {}'.format(len(movie['genres'])))
			for genre in movie['genres']:
					try:
							genreID = Genres.objects.get(pk=genre['id'])
							genreID = genre['id']
							old+=1
					except Genres.DoesNotExist:
							genreID = Genres.addGenre(genre)
							new+=1
					isGenre.addGenreToMovie(tmdbID,genreID)
			print('new: {}, old:{}'.format(new,old))
			new = 0
			old = 0
			print('companies: {}'.format(len(movie['production_companies'])))
			for company in movie['production_companies']:
					try:
							companyID = Company.objects.get(pk=company['id'])
							companyID = company['id']
							old+=1
					except Company.DoesNotExist:
							companyID = Company.addNewCompany(company)
							new+=1
					Produce.addProdutionCompany(tmdbID, companyID)
			print('new: {}, old:{}'.format(new,old))
			new = 0
			old = 0
			print('countries: {}'.format(len(movie['production_countries'])))
			for country in movie['production_countries']:
					try:
							countryID = Country.objects.get(pk=country['iso_3166_1'])
							countryID = country['iso_3166_1']
							old+=1
					except Country.DoesNotExist:
							countryID = Country.addCountry(country)
							new+=1
					ProductionCountry.addProductionCountry(tmdbID, countryID)
			print('new: {}, old:{}'.format(new,old))
			new = 0
			old = 0
			print('languages: {}'.format(len(movie['spoken_languages'])))
			for language in movie['spoken_languages']:
					try:
							languageID = Language.objects.get(pk=language['iso_639_1'])
							languageID = language['iso_639_1']
							old+=1
					except Language.DoesNotExist:
							languageID = Language.addLanguage(language)
							new+=1
					SpokenLanguage.addSpokenLanguage(tmdbID, languageID)
			print('new: {}, old:{}'.format(new,old))
			new = 0
			old = 0
			credits = movie['credits']
			print('cast: {}'.format(len(credits['cast'])))
			"""
			for personData in credits['cast']:
					try:
							person = Person.objects.get(pk=personData['id'])
							old+=1
					except Person.DoesNotExist:
							person = tmdb_api_wrap.getPersonByID(personData['id'])
							Person.addPerson(person)
							new+=1
					WorkedAsCast.addPersonToCast(personData, tmdbID)
			print('new: {}, old:{}'.format(new,old))
			new = 0
			old = 0
			print('crew: {}'.format(len(credits['crew'])))
			for personData in credits['crew']:
					try:
							person = Person.objects.get(pk=personData['id'])
							old+=1
					except Person.DoesNotExist:
							person = tmdb_api_wrap.getPersonByID(personData['id'])
							Person.addPerson(person)
							new+=1
					WorkedAsCrew.addPersonToCrew(personData, tmdbID)
			print('new: {}, old:{}'.format(new,old))
			"""
		except Exception as e:
			print("orco can")
			print(e)
			isGenre.objects.filter(movie=tmdbID).delete()
			Produce.objects.filter(movie=tmdbID).delete()
			WorkedAsCast.objects.filter(movie=tmdbID).delete()
			WorkedAsCrew.objects.filter(movie=tmdbID).delete()
			Movie.objects.filter(id=tmdbID).delete()

def lists(request):
	context = {}
	list = List.objects.all()
	context['list'] = list
	return render(request, 'movtra/lists.html', context)

def listDetail(request, id):
	listID = List.objects.get(id=id)

	movies = isIn.objects.filter(list=listID).order_by('id')
	if not movies.exists:
		watched_count = 0
	else:
		#watched_count = Movie.objects.raw('select distinct movtra_movie.* from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id='+str(id) +';')
		watched_count = Movie.objects.raw('select distinct movtra_movie.* , movtra_logentry.id as log_id from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id=' + str(id) + ' group by movtra_movie.id;')
		#watched_count = Movie.objects.raw('select movtra_movie.*, movtra_logentry.date from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id order by date desc;')
		w=0
		for wc in watched_count:
			w+=1
		
	print(watched_count)
	context = {'movies': movies, 'list': listID ,'total':len(movies), 'watched': len(list(watched_count)), 'logentry': list(watched_count)}
	return render(request, 'movtra/listDetail.html', context)

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

def letterboxdImport(file):
	ids = []
	p=0
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
	results = tmdb_api_wrap.getMovieByName(movieName)
	context = {'results': results , 'list_id': id}
	return render(request, 'movtra/listAdd.html', context)

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
	movieIDs = []
	wmovieIDs = []
	for m in movies:
		movieIDs.append(m.movie.id)
	
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
	context = {'movies': movieIDs, 'list': id ,'total':len(movieIDs), 'watched': w, 'logentry': wmovieIDs}
	#return render(request, 'movtra/editList.html', context)
	return JsonResponse(context,safe=False)
	#return HttpResponse(json.dumps(context))

def editLists(request):
	context = {}
	list = List.objects.all()
	context['list'] = list
	return render(request, 'movtra/listsEdit.html', context)

def editListsAjax(request):
	context = {}
	list = List.objects.all()
	data = serializers.serialize('json', List.objects.all(), fields=('id',))
	context['list'] = data
	#return render(request, 'movtra/listsEdit.html', context)
	return JsonResponse(context)

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

def removeMovieFromList(request, id, tmdbID):
	if request.method == 'POST':
		tmdbID = request.POST.get('tmdbID')
		print(id)
		print(tmdbID)
		print(isIn.objects.filter(list_id=id).filter(movie_id=tmdbID))
		isIn.objects.filter(list_id=id).filter(movie_id=tmdbID).delete()

	isIn.objects.filter(list_id=id).filter(movie_id=tmdbID).delete()
	return redirect(request.META['HTTP_REFERER'])

def removeDiaryEntry(request, tmdbID, diaryID):
	LogEntry.objects.filter(id=diaryID).delete()
	return redirect(request.META['HTTP_REFERER'])

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
	context = {'person': personData}
	return render(request, 'movtra/personDetail.html', context)

#TODO cache manager
# if (\wsdasd.jpg) exists use it else download and use it
# genres page 

#select movtra_movie.id
#from movtra_isgenre, movtra_movie
#where movtra_isgenre.genre_id=18 and movtra_isgenre.movie_id=movtra_movie.id;

#log movie when adding

#https://stackoverflow.com/questions/34774138/reload-table-data-in-django-without-refreshing-the-page/34775420
