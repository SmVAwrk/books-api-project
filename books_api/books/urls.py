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
    path('books/create/', BookCreateAPIView.as_view(), name='book-create'),
    path('books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('books/<int:pk>/edit/', BookEditAPIView.as_view(), name='book-edit'),

    path('authors/', AuthorsListAPIView.as_view(), name='authors'),
    path('authors/create/', AuthorCreateAPIView.as_view(), name='author-create'),
    path('authors/<int:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    path('authors/<int:pk>/edit/', AuthorEditAPIView.as_view(), name='author-edit'),
    path('authors/<int:pk>/books/', AuthorBooksListAPIView.as_view(), name='author-detail-books'),

    path('categories/', CategoriesListAPIView.as_view(), name='categories'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', CategoryEditAPIView.as_view(), name='category-edit'),
    path('categories/<int:pk>/books/', CategoryBooksAPIView.as_view(), name='category-detail-books'),

    path('libraries/', LibrariesListAPIView.as_view(), name='libraries'),
    path('libraries/<int:pk>/', LibraryDetailAPIView.as_view(), name='library-detail'),
    path('libraries/<int:pk>/books/', LibraryBooksAPIView.as_view(), name='library-detail-books'),

    path('create-session/', BookSessionCreateAPIView.as_view(), name='create-session'),
    path('sessions/', BooksSessionsListAPIView.as_view(), name='sessions'),
    path('sessions/<int:pk>/', BookSessionEditAPIView.as_view(), name='session-detail'),
    path('my-sessions/', MyBooksSessionsListAPIView.as_view(), name='my-sessions'),

    path('book-library/<int:pk>/', BookLibraryDetailAPIView.as_view(), name='book-library-detail'),

    # path('library/<int:pk>/create-session/', BookSessionFromLibraryCreate.as_view(), name='create-session-library'),

])

urlpatterns += router.urls
