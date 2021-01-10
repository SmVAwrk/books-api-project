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
    path('book/create/', BookCreateAPIView.as_view(), name='book-create'),
    path('book/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('book/<int:pk>/edit/', BookEditAPIView.as_view(), name='book-edit'),

    path('authors/', AuthorsListAPIView.as_view(), name='authors'),
    path('author/create/', AuthorCreateAPIView.as_view(), name='author-create'),
    path('author/<int:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    path('author/<int:pk>/edit/', AuthorEditAPIView.as_view(), name='author-edit'),
    path('author/<int:pk>/books/', AuthorBooksListAPIView.as_view(), name='author-detail-books'),

    path('categories/', CategoriesListAPIView.as_view(), name='categories'),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('category/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('category/<int:pk>/edit/', CategoryEditAPIView.as_view(), name='category-edit'),
    path('category/<int:pk>/books/', CategoriesBooksAPIView.as_view(), name='category-detail-books'),

    path('libraries/', LibrariesListAPIView.as_view(), name='libraries'),
    path('library/<int:pk>/', LibraryDetailAPIView.as_view(), name='library-detail'),

])

urlpatterns += router.urls
