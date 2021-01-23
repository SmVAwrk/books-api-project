from django.db.models import Count, Case, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from books.models import (
    Books, Authors, Categories,
    Libraries, UserBookSession, UserBookRelation,
    BookLibraryAvailable, UserBookOffer
)
import books.serializers as s
from books.services import UserBookOfferFilter, UserBookSessionFilter, BooksListFilter, set_book_values


class BooksViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка книг в наличии с возможностью поиска по названию книги,
    фильтрации через BooksListFilter и упорядочивания по рейтингу или лайкам.
    2. Получение экземпляра книги (с дополнительным аннотированным полем 'reading_now',
    подсчитывающим количество активных сессий с книгой).
    --- Доступно администраторам ---
    3. Создание, обновление и удаление экземпляра книги.
    """
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title', ]
    ordering_fields = ['rating', 'likes']
    filterset_class = BooksListFilter

    def get_queryset(self):
        if self.action == 'list':
            return Books.objects.filter(lib_available__available=True).select_related('author').prefetch_related(
                'categories').distinct()
        elif self.action == 'retrieve':
            return Books.objects.all().annotate(
                reading_now=Count(Case(When(session_books__is_accepted=True,
                                            session_books__is_closed=False,
                                            then=1))),
            ).select_related('author').prefetch_related('categories', 'lib_available__library')
        else:
            return Books.objects.all().select_related('author').prefetch_related('categories', 'lib_available__library')

    def get_serializer_class(self):
        if self.action == 'list':
            return s.BooksListSerializer
        elif self.action == 'retrieve':
            return s.BooksDetailSerializer
        else:
            return s.BookCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        return (permissions.IsAdminUser(),)


class AuthorsViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка авторов с возможностью поиска по фамилии и имени.
    2. Получение экземпляра автора.
    3. Получение списка всех книг определенного автора с возможностью поиска по названию.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра автора.
    """
    queryset = Authors.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return s.AuthorsListSerializer
        elif self.action == 'retrieve':
            return s.AuthorDetailSerializer
        elif self.action == 'get_books':
            return s.BooksListSerializer
        else:
            return s.AuthorCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(),)
        return (permissions.IsAdminUser(),)

    @action(
        detail=True,
        url_name='books',
        url_path='books',
        queryset=Books.objects.all(),
        search_fields=['title', ]
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг автора"""
        books_by_author = Books.objects.filter(author=self.kwargs['pk']).select_related('author').prefetch_related(
            'categories')
        queryset = self.filter_queryset(books_by_author)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoriesViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка категорий с возможностью поиска по названию.
    2. Получение экземпляра категории.
    3. Получение списка всех книг определенной категории с возможностью поиска по названию.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра категории.
    """
    queryset = Categories.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return s.CategoriesListSerializer
        elif self.action == 'retrieve':
            return s.CategoryDetailSerializer
        elif self.action == 'get_books':
            return s.BooksListSerializer
        else:
            return s.CategoryCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(),)
        return (permissions.IsAdminUser(),)

    @action(
        detail=True,
        url_name='books',
        url_path='books',
        queryset=Books.objects.all()
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг категории"""
        books_by_author = Books.objects.filter(categories=self.kwargs['pk']).select_related('author').prefetch_related(
            'categories')
        queryset = self.filter_queryset(books_by_author)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LibrariesViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка библиотек с возможностью поиска по названию.
    2. Получение экземпляра библиотеки.
    3. Получение списка всех доступных книг в определенной библиотеке с возможностью поиска по названию.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра библиотеки.
    """
    queryset = Libraries.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return s.LibrariesListSerializer
        elif self.action == 'retrieve':
            return s.LibraryDetailSerializer
        elif self.action == 'get_books':
            return s.BooksListSerializer
        else:
            return s.LibraryCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(), )
        else:
            return (permissions.IsAdminUser(), )

    @action(
        detail=True,
        url_name='books',
        url_path='books',
        queryset=Books.objects.all(),
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг доступных в определенной библиотеке"""
        books_by_author = Books.objects.filter(lib_available__library=self.kwargs['pk']).select_related(
            'author').prefetch_related('categories')
        queryset = self.filter_queryset(books_by_author)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MySessionsViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно авторизованным пользователям ---
    1. Получение списка своих сессий с возможностью фильтрации по закрытым и принятым сессиям.
    2. Получение экземпляра своей сессии.
    3. Создание экземпляра сессии.
    """
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [DjangoFilterBackend, ]
    filter_fields = ['is_accepted', 'is_closed']

    def get_serializer_class(self):
        if self.action == 'list':
            return s.MyBooksSessionsListSerializer
        elif self.action == 'retrieve':
            return s.MyBooksSessionDetailSerializer
        else:
            return s.BooksSessionCreateSerializer

    def get_queryset(self):
        return UserBookSession.objects.filter(user=self.request.user).select_related('user', 'library')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSessionsViewSet(mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно администраторам ---
    1. Получение списка пользовательских сессий с возможностью поиска по названию книги,
    имени пользователя и названию библиотеки и фильтрации через UserBookSessionFilter.
    2. Получение экземпляра сессии.
    3. Обновление и удаление экземпляра сессии.
    """
    queryset = UserBookSession.objects.all().select_related('user', 'library').prefetch_related('books')
    permission_classes = (permissions.IsAdminUser, )
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['books__title', 'user__username', 'library__title']
    filterset_class = UserBookSessionFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return s.UserBooksSessionsListSerializer
        elif self.action == 'retrieve':
            return s.MyBooksSessionDetailSerializer
        else:
            return s.UserBooksSessionsEditSerializer


class BooksLibrariesAvailableViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно администраторам ---
    1. Получение списка экземпляров BookLibraryAvailable с возможностью фильтрации по книге и библиотеке.
    2. Получение экземпляра BookLibraryAvailable.
    3. Создание, обновление и удаление экземпляра BookLibraryAvailable.
    """
    queryset = BookLibraryAvailable.objects.all().select_related('book', 'library')
    permission_classes = (permissions.IsAdminUser, )
    filter_backends = [DjangoFilterBackend, ]
    filter_fields = ['book', 'library']

    def get_serializer_class(self):
        if self.action == 'list':
            return s.BooksLibrariesAvailableListSerializer
        elif self.action == 'retrieve':
            return s.BooksLibrariesAvailableDetailSerializer
        else:
            return s.BooksLibrariesAvailableEditSerializer


class UserBookRelationViewSet(mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно авторизованным пользователям ---
    1. Создание своего экземпляра отношения пользователя к книги.
    2. Обновление своего экземпляра отношения пользователя к книги.
    """
    permission_classes = (permissions.IsAuthenticated, )
    queryset = UserBookRelation.objects.all()
    serializer_class = s.UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, self.created = UserBookRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj

    def perform_update(self, serializer):
        """Обновления полей рейтинга, лайков и закладок книги"""
        serializer.save()
        set_book_values(serializer, self.created)


class MyOffersViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно авторизованным пользователям ---
    1. Получение списка своих предложений с возможностью фильтрации по закрытым и принятым предложениям.
    2. Получение экземпляра своего предложения.
    3. Создание экземпляра предложения.
    """
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [DjangoFilterBackend, ]
    filter_fields = ['is_accepted', 'is_closed']

    def get_serializer_class(self):
        if self.action == 'list':
            return s.MyBooksOffersListSerializer
        elif self.action == 'retrieve':
            return s.MyBooksOfferDetailSerializer
        else:
            return s.MyBooksOfferCreateSerializer

    def get_queryset(self):
        return UserBookOffer.objects.filter(user=self.request.user).select_related('user', 'library')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserOffersViewSet(mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно администраторам ---
    1. Получение списка пользовательских предложений с возможностью поиска по описанию книг,
    имени пользователя и названию библиотеки и фильтрации через UserBookOfferFilter.
    2. Получение экземпляра предложения.
    3. Обновление и удаление экземпляра предложения.
    """
    queryset = UserBookOffer.objects.all().select_related('user', 'library')
    permission_classes = (permissions.IsAdminUser, )
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['books_description', 'user__username', 'library__title']
    filterset_class = UserBookOfferFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return s.UserBooksOffersListSerializer
        elif self.action == 'retrieve':
            return s.MyBooksOfferDetailSerializer
        else:
            return s.UserBooksOfferEditSerializer


class MyBookmarksViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно авторизованным пользователям ---
    1. Получение списка своих закладок с возможностью поиска по названию.
    2. Получение экземпляра книги из закладок.
    """
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [SearchFilter, ]
    search_fields = ['title', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return s.BooksListSerializer
        return s.BooksDetailSerializer

    def get_queryset(self):
        return Books.objects.filter(userbookrelation__user=self.request.user,
                                    userbookrelation__in_bookmarks=True).select_related(
            'author').prefetch_related('categories')
