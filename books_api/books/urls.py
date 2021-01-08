from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from books.views import *
from books_api import settings

router = SimpleRouter()
# router.register('books', BookDetailAPIView)
# router.register('authors', AuthorsViewSet)

urlpatterns = format_suffix_patterns([
    path('', api_root),
    path('books/', BooksListAPIView.as_view(), name='books'),
    path('authors/', AuthorsListAPIView.as_view()),
    path('categories/', CategoriesListAPIView.as_view()),
    path('libraries/', LibrariesListAPIView.as_view()),
    path('book/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('book/create/', BookCreateAPIView.as_view()),
])

urlpatterns += router.urls