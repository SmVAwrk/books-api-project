from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from books.views import *
from books_api import settings

router = DefaultRouter()
router.register('books', BooksViewSet, basename='book')
router.register('authors', AuthorsViewSet, basename='author')
router.register('categories', CategoriesViewSet, basename='category')
router.register('libraries', LibrariesViewSet, basename='library')
router.register('my-sessions', MySessionsViewSet, basename='my-session')
router.register('my-offers', MyOffersViewSet, basename='my-offer')
router.register('my-bookmarks', MyBookmarksViewSet, basename='my-bookmark')

router.register('available', BooksLibrariesAvailableViewSet, basename='available')
router.register('user-sessions', UserSessionsViewSet, basename='user-session')
router.register('user-offers', UserOffersViewSet, basename='user-offer')

router.register('book-relation', UserBookRelationViewSet, basename='book-relation')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
