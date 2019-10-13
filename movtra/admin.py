from django.contrib import admin

from .models import Movie, Genres, isGenre, WorkedAsCast, WorkedAsCrew, Company, Produce, Country, ProductionCountry, Language, SpokenLanguage, LogEntry, isIn

# Register your models here.

admin.site.register(Movie)
admin.site.register(Genres)
admin.site.register(isGenre)
admin.site.register(WorkedAsCast)
admin.site.register(WorkedAsCrew)
admin.site.register(Company)
admin.site.register(Produce)
admin.site.register(Country)
admin.site.register(ProductionCountry)
admin.site.register(Language)
admin.site.register(SpokenLanguage)
admin.site.register(LogEntry)
admin.site.register(isIn)