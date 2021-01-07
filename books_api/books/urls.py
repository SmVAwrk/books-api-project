from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from books.views import *
from books_api import settings

router = SimpleRouter()
# router.register('books', BookDetailAPIView)
# router.register('authors', AuthorsViewSet)

urlpatterns = [
    path('books/', BooksListAPIView.as_view()),
    path('authors/', AuthorsListAPIView.as_view()),
    path('categories/', CategoriesListAPIView.as_view()),
    path('libraries/', LibrariesListAPIView.as_view()),
    path('book/<int:pk>/', BookDetailAPIView.as_view()),
    path('book/create/', BookCreateAPIView.as_view()),
]

urlpatterns += router.urls