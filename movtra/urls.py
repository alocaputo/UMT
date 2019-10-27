from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'movtra'
urlpatterns = [
	path('', views.index, name='index'),
	path('all', views.all, name='all'),
	path('upcoming', views.upcoming, name='upcoming'),
	path('nowplaying', views.nowplaying, name='nowplaying'),
	path('stats', views.stats, name='stats'),
	path('movie/<int:tmdbID>/', views.detail, name='detail'),
	path('movie/<int:tmdbID>/removeDiaryEntry/<int:diaryID>', views.removeDiaryEntry, name='removeDiaryEntry'),
	path('person/<int:tmdbID>/', views.personDetail, name='personDetail'),
	path('movie/<int:tmdbID>/editReview', views.editReview, name='editReview'),
	path('movie/<int:tmdbID>/saveReview', views.saveReview, name='saveReview'),
	path('lists/', views.lists, name='lists'),
	path('lists/editLists/', views.editLists, name='editLists'),

	url(r'^removeListsGET/$', views.removeListsGET, name='removeListsGET'),

	path('lists/<int:id>', views.listDetail, name='listDetail'),
	path('lists/<int:id>/editList', views.editList, name='editList'),
	path('lists/<int:id>/importList', views.importList, name='importList'),
	path('lists/<int:id>/addToList', views.addToList, name='addToList'),

	url(r'^removeMovieFromListGET/$', views.removeMovieFromListGET, name='removeMovieFromListGET'),

	path('movie/<int:tmdbID>/updateData', views.updateData, name='updateData'),

	path('lists/<int:id>/addToList/addMovieToList', views.addMovieToList, name='addMovieToList'),
	path('lists/newList', views.newList, name='newList'),
	url(r'^logMovie', views.logMovie, name='logMovie'),
	path('results/<str:query>/<int:page>', views.results, name='results'),

]