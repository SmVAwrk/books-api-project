from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework import generics

from books.models import Books, Authors, Categories, Libraries
from books.permissions import IsAuthorOrAdminOrReadOnly
from books.serializers import BooksListSerializer, AuthorsListSerializer, CategoriesListSerializer, \
    LibrariesListSerializer, BooksDetailSerializer, BooksCreateSerializer


class BooksListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг
    """
    queryset = Books.objects.all().order_by('-created_at')
    serializer_class = BooksListSerializer


class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра (и редактирования или удаления (если пользователь админ или автор))
    """
    queryset = Books.objects.all().select_related('owner_user', 'author').prefetch_related('categories')
    serializer_class = BooksDetailSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly, )


class BookCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания книги (только авторизованным пользователем)
    """
    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Метод для автоматического добавления владельца книги"""
        serializer.save(owner_user=self.request.user)


class AuthorsListAPIView(generics.ListAPIView):
    queryset = Authors.objects.all().order_by('last_name')
    serializer_class = AuthorsListSerializer


class CategoriesListAPIView(generics.ListAPIView):
    queryset = Categories.objects.all().order_by('title')
    serializer_class = CategoriesListSerializer


class LibrariesListAPIView(generics.ListAPIView):
    queryset = Libraries.objects.all().order_by('title')
    serializer_class = LibrariesListSerializer
