from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from books.models import Books, Authors, Categories, Libraries
from books.permissions import IsAuthorOrAdminOrReadOnly
from books.serializers import BooksListSerializer, AuthorsListSerializer, CategoriesListSerializer, \
    LibrariesListSerializer, BooksDetailSerializer, BooksCreateSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'books': reverse('books', request=request, format=format)
    })


class BooksListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг
    """
    queryset = Books.objects.all().select_related('author')
    serializer_class = BooksListSerializer
    permissions_classes = (permissions.AllowAny, )


class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра (и редактирования или удаления (если пользователь админ или автор))
    """
    queryset = Books.objects.all().select_related('owner', 'author').prefetch_related('categories')
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
        serializer.save(owner=self.request.user)


class AuthorsListAPIView(generics.ListAPIView):
    queryset = Authors.objects.all().order_by('last_name')
    serializer_class = AuthorsListSerializer


class CategoriesListAPIView(generics.ListAPIView):
    queryset = Categories.objects.all().order_by('title')
    serializer_class = CategoriesListSerializer


class LibrariesListAPIView(generics.ListAPIView):
    queryset = Libraries.objects.all().order_by('title')
    serializer_class = LibrariesListSerializer
