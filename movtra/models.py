from django.db import models
from datetime import datetime

# Create your models here.

class Movie(models.Model):
	id = models.CharField(primary_key=True, max_length=50)
	adult = models.BooleanField()
	belongs_to_collection = models.IntegerField(null=True, blank=True)
	budget = models.IntegerField(null=True, blank=True)
	homepage = models.CharField(null=True, blank=True, max_length=100)
	imdb_id = models.CharField(null=True, blank=True, max_length=100)
	original_language = models.CharField(blank=True, null=True, max_length=100)
	original_title = models.CharField(blank=True, null=True, max_length=100)
	overview = models.TextField()
	popularity = models.DecimalField(max_digits=10, null=True, decimal_places=6, blank=True)
	backdrop_path = models.CharField(null=True, blank=True, max_length=100)
	poster_path = models.CharField(null=True, blank=True, max_length=100)
	release_date = models.DateField(blank=True, null=True)
	revenue = models.IntegerField(null=True, blank=True)
	runtime = models.IntegerField(null=True, blank=True)
	status = models.CharField(blank=True, null=True, max_length=100)
	tagline = models.CharField(blank=True, null=True, max_length=100)
	title = models.CharField(max_length=100)
	video = models.BooleanField()
	vote_average = models.DecimalField(max_digits=3, null=True, decimal_places=1 , blank=True, default=0)
	vote_count = models.IntegerField(null=True, blank=True)

	last_updated = models.DateTimeField(auto_now_add=True, blank=True)

	#Seen_entry(id,date,vote)
	#status_watched = models.BooleanField(default=False)
	#date_seen = models.DateTimeField(blank=True, null=True)
	#vote_self = models.DecimalField(max_digits=2, null=True, decimal_places=0 , blank=True, default=0)



	def __str__(self):
		return self.title

	def addShow(data):
			try:
				movie = Movie.objects.get(id=data['id'])
			except Movie.DoesNotExist:
				movie = None
			if movie is None:
				movie = Movie()
				movie.id = data['id']
				
			movie.adult = data['adult']
			if( data['belongs_to_collection'] is not None):
				movie.belongs_to_collection = data['belongs_to_collection']['id']
			#movie.belongs_to_collection = False
			movie.budget = data['budget']
			movie.homepage = data['homepage']
			movie.imdb_id = data['imdb_id']
			movie.original_language = data['original_language']
			movie.original_title = data['original_title']
			movie.overview = data['overview']
			movie.popularity = data['popularity']
			movie.backdrop_path = data['backdrop_path']
			movie.poster_path = data['poster_path']
			movie.release_date = data['release_date']
			movie.revenue = data['revenue']
			movie.runtime = data['runtime']
			movie.status = data['status']
			movie.tagline = data['tagline']
			movie.title = data['title']
			movie.video = data['video']
			movie.vote_average = data['vote_average']
			movie.vote_count = data['vote_count']
			#print(movie)
			movie.save()
			return movie

class List(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	def addShow(name):
		list = List()
		list.name = name
		list.save()

class isIn(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	list = models.ForeignKey(List, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("movie", "list")

	def __str__(self):
		return self.list.name + " | " + self.movie.title

	def addShow(movieID, listID):
		isin = isIn()
		isin.movie = Movie.objects.get(id=movieID)
		isin.list = List.objects.get(id=listID)
		isin.save()

class Genres(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(null=False, blank=False, max_length=50)

	def __str__(self):
		return self.name

	def addGenre(genre):
		newGenre = Genres()
		newGenre.id = genre['id']
		newGenre.name = genre['name']
		newGenre.save()
		return newGenre.id

class isGenre(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	genre = models.ForeignKey(Genres, on_delete=models.DO_NOTHING)

	def __str__(self):
		return self.movie.title + " | " + self.genre.name

	def addGenreToMovie(movie, genre):
		isgenre = isGenre()
		isgenre.movie = Movie.objects.get(id=movie)
		isgenre.genre = Genres.objects.get(id=genre)
		isgenre.save()
"""
class Person(models.Model):
	id = models.IntegerField(primary_key=True)
	birthday = models.DateField(null=True, blank=True)
	deathday = models.DateField(null=True, blank=True)
	name = models.CharField(blank=True, null=True, max_length=100)
	gender = models.IntegerField(null=True, blank=True)
	biography = models.TextField()
	popularity = models.DecimalField(max_digits=10, null=True, decimal_places=6, blank=True)
	#place_of_birth = models.CharField(blank=True, null=True, max_length=100)
	profile_path = models.CharField(blank=True, null=True, max_length=100)
	adult = models.BooleanField()
	imdb_id = models.CharField(null=True, blank=True, max_length=100)
	homepage = models.CharField(null=True, blank=True, max_length=100)

	def __str__(self):
		return self.name

	def addPerson(data):
		newPerson = Person()
		newPerson.id = data['id']
		newPerson.birthday = data['birthday']
		newPerson.deathday = data['deathday']
		newPerson.name = data['name']
		newPerson.gender = data['gender']
		newPerson.biography = data['biography']
		newPerson.place_of_birth = data['place_of_birth']
		newPerson.popularity = data['popularity']
		newPerson.adult = data['adult']
		newPerson.imdb_id = data['imdb_id']
		newPerson.homepage = data['homepage']
		newPerson.save()
"""
class WorkedAsCast(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	cast_id = models.IntegerField(null=True, blank=True)
	character = models.CharField(blank=True, null=True, max_length=100)
	credit_id = models.CharField(max_length=100)
	gender = models.IntegerField(null=True, blank=True)
	person_id = models.IntegerField()
	#person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
	name = models.CharField(blank=True, null=True, max_length=100)
	order = models.IntegerField(null=True, blank=True)
	profile_path = models.CharField(blank=True, null=True, max_length=100)

	def __str__(self):
		return self.movie.title + " | " + self.person_id

	def addPersonToCast(role, movieID):
		newRole = WorkedAsCast()
		newRole.movie = Movie.objects.get(id=movieID)
		#newRole.person = Person.objects.get(id=role['id'])
		newRole.cast_id = role['cast_id']
		newRole.character = role['character']
		newRole.credit_id = role['credit_id']
		newRole.gender = role['gender']
		newRole.person_id = role['id']
		newRole.name = role['name']
		newRole.order = role['order']
		newRole.profile_path = role['profile_path']
		newRole.save()

class WorkedAsCrew(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	#person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
	credit_id = models.CharField(max_length=100)
	department = models.CharField(blank=True, null=True, max_length=100)
	gender = models.IntegerField(null=True, blank=True)
	person_id = models.IntegerField()
	job = models.CharField(blank=True, null=True, max_length=100)
	name = models.CharField(blank=True, null=True, max_length=100)
	profile_path = models.CharField(blank=True, null=True, max_length=100)




	def __str__(self):
		return self.movie.title + " | " + self.person_id

	def addPersonToCrew(role, movieID):
		newJob = WorkedAsCrew()
		newJob.movie = Movie.objects.get(id=movieID)
		#newJob.person = Person.objects.get(id=role['id'])
		newJob.credit_id = role['credit_id']
		newJob.department = role['department']
		newJob.gender = role['gender']
		newJob.person_id = role['id']
		newJob.job = role['job']
		newJob.name = role['name']
		newJob.profile_path = role['profile_path']
		newJob.save()

class Company(models.Model):
	id = models.IntegerField(primary_key=True)
	logo_path = models.CharField(null=True, blank=True, max_length=50)
	name = models.CharField(null=True, blank=True, max_length=50)
	origin_country = models.CharField(null=True, blank=True, max_length=50)

	def __str__(self):
		return self.name

	def addNewCompany(data):
		newCompany = Company()
		newCompany.id = data['id']
		newCompany.logo_path = data['logo_path']
		newCompany.name = data['name']
		newCompany.origin_country = data['origin_country']
		newCompany.save()
		return newCompany.id

class Produce(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)

	def __str__(self):
		return self.movie.title + " | " + self.company.name

	def addProdutionCompany(movieID, companyID):
		newrodutionCompany = Produce()
		newrodutionCompany.movie = Movie.objects.get(id=movieID)
		newrodutionCompany.company = Company.objects.get(id=companyID)
		newrodutionCompany.save()

class Country(models.Model):
	iso_3166_1 = models.CharField(primary_key=True, max_length=50)
	name = models.CharField(null=True, blank=True, max_length=50)

	def __str__(self):
		return self.name

	def addCountry(data):
		newCountry = Country()
		newCountry.iso_3166_1 = data['iso_3166_1']
		newCountry.name = data['name']
		newCountry.save()
		return newCountry.iso_3166_1

class ProductionCountry(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)

	def __str__(self):
		return self.movie.title + " | " + self.country.name

	def addProductionCountry(movieID, countryID):
		newProductionCountry = ProductionCountry()
		newProductionCountry.movie = Movie.objects.get(id=movieID)
		newProductionCountry.country = Country.objects.get(iso_3166_1=countryID)
		newProductionCountry.save()

class Language(models.Model):
	iso_639_1 = models.CharField(primary_key=True, max_length=50)
	name = models.CharField(null=True, blank=True, max_length=50)

	def __str__(self):
		return self.name

	def addLanguage(data):
		newLanguage = Language()
		newLanguage.iso_639_1 = data['iso_639_1']
		newLanguage.name = data['name']
		newLanguage.save()
		return newLanguage.iso_639_1

class SpokenLanguage(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)

	def __str__(self):
		return self.movie.title + " | " + self.language.name

	def addSpokenLanguage(movieID, languageID):
		newSpokenLanguage = SpokenLanguage()
		newSpokenLanguage.movie = Movie.objects.get(id=movieID)
		newSpokenLanguage.language = Language.objects.get(iso_639_1=languageID)
		newSpokenLanguage.save()

class LogEntry(models.Model):
	movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
	date = models.DateField(blank=True, null=True)
	rating = models.DecimalField(max_digits=3, null=True, decimal_places=1 , blank=True, default=0)
	review = models.TextField(blank=True)

	def __str__(self):
		if self.date != None:
			return self.date.strftime('%d/%m/%Y') + " | " + self.movie.title + " | " +  str(self.rating)
		else:
			return "No date available | " + self.movie.title + " | " + str(self.rating)
	def addLogEntry(data):
		newLogEntry = LogEntry()
		newLogEntry.movie = Movie.objects.get(id=data['tmdbID'])
		if data['date'] != '':
			newLogEntry.date = data['date']
		if data['rating'] != None:
			newLogEntry.rating = float(data['rating'])
		else: # empty => 0
			newLogEntry.rating = float(0)
		newLogEntry.review = data['review']
		newLogEntry.save()
		return newLogEntry.movie.id

	#TODO see listDelete
	def deleteEntry(entryID):
		instance = LogEntry.objects.get(id=entryID)
		instance.delete()

