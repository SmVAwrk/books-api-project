from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from books.views import BooksAPIView, AuthorsAPIView, CategoriesAPIView, LibrariesAPIView
from books_api import settings

router = SimpleRouter()
# router.register('books', BooksViewSet)
# router.register('authors', AuthorsViewSet)

urlpatterns = [
    path('books/', BooksAPIView.as_view()),
    path('authors/', AuthorsAPIView.as_view()),
    path('categories/', CategoriesAPIView.as_view()),
    path('libraries/', LibrariesAPIView.as_view()),
]

urlpatterns += router.urls