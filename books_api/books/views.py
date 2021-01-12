from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from books.models import Books, Authors, Categories, Libraries, UserBookSession
from books.permissions import IsOwnerOrAdmin, IsAdminOrOwnerReadOnly
from books.serializers import *


@api_view(['GET'])
def api_root(request, format=None):
    """Представление для корня api"""
    return Response({
        'books': reverse('books', request=request, format=format),
        'authors': reverse('authors', request=request, format=format),
        'categories': reverse('categories', request=request, format=format),
        'libraries': reverse('libraries', request=request, format=format),
        'create-session': reverse('create-session', request=request, format=format),
        'sessions(admin)': reverse('sessions', request=request, format=format),
        'my-sessions': reverse('my-sessions', request=request, format=format),
    })


class BooksListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг в наличии
    """
    queryset = Books.objects.filter(lib_available__available=True
                                    ).select_related('author').prefetch_related('categories').distinct()
    serializer_class = BooksListSerializer
    permissions_classes = (permissions.AllowAny, )
    filter_backends = [SearchFilter]
    # filter_fields = ['author', 'categories']
    search_fields = ['title']


class BookDetailAPIView(generics.RetrieveAPIView):
    """
    Представление для просмотра информации о книге
    """
    queryset = Books.objects.all().select_related('owner', 'author').prefetch_related('categories')
    serializer_class = BooksDetailSerializer
    permission_classes = (permissions.IsAuthenticated, )


class BookCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания книги (только авторизованным пользователем)
    """
    queryset = Books.objects.all()
    serializer_class = BookCreateSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Метод для автоматического добавления владельца книги"""
        serializer.save(owner=self.request.user)


class BookEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для редактирования или удаления книги (права только для владелеца или админа)
    """
    queryset = Books.objects.all()
    serializer_class = BookCreateSerializer
    permission_classes = (IsOwnerOrAdmin, )


# class BookSessionFromLibraryCreate(generics.CreateAPIView):
#     """
#     Представление для создания сессии с книгой
#     """
#     queryset = UserBookSession.objects.all()
#     serializer_class = BookSessionCreateFromLibrarySerializer
#     permission_classes = (permissions.IsAuthenticated, )
#
#     def perform_create(self, serializer):
#         """Метод для автоматического добавления владельца книги"""
#         serializer.save(
#             user=self.request.user,
#             library=Libraries.objects.get(pk=self.kwargs['pk'])
#         )

class BooksSessionsListAPIView(generics.ListAPIView):
    """
    Представление для просмотра сессий с книгами
    """
    queryset = UserBookSession.objects.filter(is_closed=False)
    serializer_class = BooksSessionsListSerializer
    permission_classes = (permissions.IsAdminUser, )


class MyBooksSessionsListAPIView(generics.ListAPIView):
    """
    Представление для просмотра своих сессий с книгами
    """
    queryset = UserBookSession.objects.filter(is_closed=False)
    serializer_class = BooksSessionsListSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return UserBookSession.objects.filter(user=self.request.user)


class BookSessionCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания сессии с книгой
    """
    queryset = UserBookSession.objects.all()
    serializer_class = BookSessionCreateSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Метод для автоматического добавления пользователя сессии"""
        serializer.save(
            user=self.request.user,
        )


class BookSessionEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра сессии (для пользовтаеля)
    и изменения (для админа)
    """
    queryset = UserBookSession.objects.all()
    serializer_class = BookSessionEditSerializer
    permission_classes = (IsAdminOrOwnerReadOnly, )

    # def perform_update(self, serializer):
    #     """Метод для автоматического добавления владельца книги"""
    #     if serializer.validated_data['is_accepted']:
    #         ava_value = BookLibraryQuantity.objects.get(book=self.kwargs['book'], library=self.kwargs['library']).available
    #         ava_value = F('available') - 1
    #         ava_value.save()
    #         ava_value.refresh_from_db()
    #     instance = serializer.save()


# class BookSessionCreate(APIView):
#     """
#     Представление для создания сессии с книгой
#     """
#     def post(self, request, pk, format=None):
#         serializer = BookSessionCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(
#                 user=self.request.user,
#                 library=Libraries.objects.get(pk=self.kwargs[pk])
#             )
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorsListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка авторов
    """
    queryset = Authors.objects.all()
    serializer_class = AuthorsListSerializer
    permissions_classes = (permissions.AllowAny,)
    filter_backends = [SearchFilter, ]
    search_fields = ['first_name', 'last_name']


class AuthorDetailAPIView(generics.RetrieveAPIView):
    """
    Представление для просмотра информации об авторе
    """
    queryset = Authors.objects.all()
    serializer_class = AuthorDetailSerializer
    permission_classes = (permissions.IsAuthenticated, )


class AuthorCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания автора (только авторизованным пользователем)
    """
    queryset = Authors.objects.all()
    serializer_class = AuthorCreateSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Метод для автоматического добавления владельца книги"""
        serializer.save(owner=self.request.user)


class AuthorEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для редактирования или удаления автора (права только для владелеца или админа)
    """
    queryset = Authors.objects.all()
    serializer_class = AuthorCreateSerializer
    permission_classes = (IsOwnerOrAdmin, )


class AuthorBooksListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг определенного автора
    """
    queryset = Books.objects.all().select_related('author')
    serializer_class = BooksListSerializer
    permissions_classes = (permissions.IsAuthenticated, )
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Books.objects.filter(author=self.kwargs['pk']).select_related('author').prefetch_related('categories')


class CategoriesListAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка категорий
    """
    queryset = Categories.objects.all()
    serializer_class = CategoriesListSerializer
    permissions_classes = (permissions.AllowAny,)


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """
    Представление для просмотра информации о категории
    """
    queryset = Categories.objects.all()
    serializer_class = CategoryDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CategoryCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания категории (только авторизованным пользователем)
    """
    queryset = Categories.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = (permissions.IsAdminUser, )

    def perform_create(self, serializer):
        """Метод для автоматического добавления владельца книги"""
        serializer.save(owner=self.request.user)


class CategoryEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для редактирования или удаления категории (права только для владелеца или админа)
    """
    queryset = Categories.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = (permissions.IsAdminUser, )


class CategoryBooksAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг определенной категории
    """
    queryset = Books.objects.all().select_related('author')
    serializer_class = BooksListSerializer
    permissions_classes = (permissions.IsAuthenticated, )
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Books.objects.filter(categories__in=[self.kwargs['pk']]).select_related('author').prefetch_related('categories')


class LibrariesListAPIView(generics.ListAPIView):
    """
    Представление для просмотра библиотек
    """
    queryset = Libraries.objects.all()
    serializer_class = LibrariesListSerializer
    permissions_classes = (permissions.AllowAny,)


class LibraryDetailAPIView(generics.RetrieveAPIView):
    """
    Представление для просмотра информации о библиотеке
    """
    queryset = Libraries.objects.all()
    serializer_class = LibraryDetailSerializer
    permission_classes = (permissions.IsAuthenticated, )


class LibraryBooksAPIView(generics.ListAPIView):
    """
    Представление для просмотра списка книг определенной библотеки
    """
    queryset = Books.objects.all().select_related('author')
    serializer_class = BooksListSerializer
    permissions_classes = (permissions.IsAuthenticated, )
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Books.objects.filter(lib_available__library=self.kwargs['pk']).select_related('author').prefetch_related('categories')


class BookLibraryDetailAPIView(generics.RetrieveAPIView):
    queryset = BookLibraryAvailable.objects.all()
    serializer_class = BookLibrarySerializer
    permissions_classes = (permissions.AllowAny, )
