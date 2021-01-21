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
from books.serializers import (
    BooksListSerializer, BooksDetailSerializer, BookCreateSerializer, AuthorsListSerializer,
    AuthorDetailSerializer, AuthorCreateSerializer, CategoriesListSerializer, CategoryDetailSerializer,
    CategoryCreateSerializer, LibrariesListSerializer, LibraryDetailSerializer, LibraryCreateSerializer,
    MyBooksSessionsListSerializer, MyBooksSessionDetailSerializer, BooksSessionCreateSerializer,
    UserBooksSessionsListSerializer, UserBooksSessionsEditSerializer, BooksLibrariesAvailableListSerializer,
    BooksLibrariesAvailableDetailSerializer, BooksLibrariesAvailableEditSerializer, UserBookRelationSerializer,
    MyBooksOffersListSerializer, MyBooksOfferDetailSerializer, MyBooksOfferCreateSerializer,
    UserBooksOffersListSerializer, UserBooksOfferEditSerializer
)
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
            return BooksListSerializer
        elif self.action == 'retrieve':
            return BooksDetailSerializer
        else:
            return BookCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        else:
            return (permissions.IsAdminUser(),)


class AuthorsViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка авторов с возможностью поиска по фамилии и имени.
    2. Получение экземпляра автора.
    3. Получение списка всех книг определенного автора.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра автора.
    """
    queryset = Authors.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuthorsListSerializer
        elif self.action == 'retrieve':
            return AuthorDetailSerializer
        elif self.action == 'get_books':
            return BooksListSerializer
        else:
            return AuthorCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(),)
        else:
            return (permissions.IsAdminUser(),)

    @action(
        detail=True,
        url_name='books',
        url_path='books',
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг автора"""
        books_by_author = Books.objects.filter(author=self.get_object()).select_related('author').prefetch_related(
            'categories')
        page = self.paginate_queryset(books_by_author)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books_by_author, many=True)
        return Response(serializer.data)


class CategoriesViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка категорий с возможностью поиска по названию.
    2. Получение экземпляра категории.
    3. Получение списка всех книг определенной категории.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра категории.
    """
    queryset = Categories.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoriesListSerializer
        elif self.action == 'retrieve':
            return CategoryDetailSerializer
        elif self.action == 'get_books':
            return BooksListSerializer
        else:
            return CategoryCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(),)
        else:
            return (permissions.IsAdminUser(),)

    @action(
        detail=True,
        url_name='books',
        url_path='books'
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг категории"""
        books_by_category = Books.objects.filter(categories=self.get_object()).select_related(
            'author').prefetch_related('categories')
        page = self.paginate_queryset(books_by_category)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books_by_category, many=True)
        return Response(serializer.data)


class LibrariesViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно всем пользователям ---
    1. Получение списка библиотек с возможностью поиска по названию.
    2. Получение экземпляра библиотеки.
    3. Получение списка всех доступных книг в определенной библиотеке.
    --- Доступно администраторам ---
    4. Создание, обновление и удаление экземпляра библиотеки.
    """
    queryset = Libraries.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return LibrariesListSerializer
        elif self.action == 'retrieve':
            return LibraryDetailSerializer
        elif self.action == 'get_books':
            return BooksListSerializer
        else:
            return LibraryCreateSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_books'):
            return (permissions.AllowAny(), )
        else:
            return (permissions.IsAdminUser(), )

    @action(
        detail=True,
        url_name='books',
        url_path='books'
    )
    def get_books(self, request, pk=None):
        """Создание кастомного действия для просмотра списка книг доступных в определенной библиотеке"""
        books_by_library = Books.objects.filter(lib_available__library=self.get_object()).select_related(
            'author').prefetch_related('categories')
        page = self.paginate_queryset(books_by_library)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books_by_library, many=True)
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
            return MyBooksSessionsListSerializer
        elif self.action == 'retrieve':
            return MyBooksSessionDetailSerializer
        else:
            return BooksSessionCreateSerializer

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
    имени пользователя и названию бибилотеки и фильтрации через UserBookSessionFilter.
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
            return UserBooksSessionsListSerializer
        elif self.action == 'retrieve':
            return MyBooksSessionDetailSerializer
        else:
            return UserBooksSessionsEditSerializer


class BooksLibrariesAvailableViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для следующих действий:
    --- Доступно администраторам ---
    1. Получение списка экземпляров BookLibraryAvailable с возможностью фильтрации по книге и бибилотеке.
    2. Получение экземпляра BookLibraryAvailable.
    3. Создание, обновление и удаление экземпляра BookLibraryAvailable.
    """
    queryset = BookLibraryAvailable.objects.all().select_related('book', 'library')
    permission_classes = (permissions.IsAdminUser, )
    filter_backends = [DjangoFilterBackend, ]
    filter_fields = ['book', 'library']

    def get_serializer_class(self):
        if self.action == 'list':
            return BooksLibrariesAvailableListSerializer
        elif self.action == 'retrieve':
            return BooksLibrariesAvailableDetailSerializer
        else:
            return BooksLibrariesAvailableEditSerializer


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
    serializer_class = UserBookRelationSerializer
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
            return MyBooksOffersListSerializer
        elif self.action == 'retrieve':
            return MyBooksOfferDetailSerializer
        else:
            return MyBooksOfferCreateSerializer

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
    имени пользователя и названию бибилотеки и фильтрации через UserBookOfferFilter.
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
            return UserBooksOffersListSerializer
        elif self.action == 'retrieve':
            return MyBooksOfferDetailSerializer
        else:
            return UserBooksOfferEditSerializer


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
            return BooksListSerializer
        else:
            return BooksDetailSerializer

    def get_queryset(self):
        return Books.objects.filter(userbookrelation__user=self.request.user,
                                    userbookrelation__in_bookmarks=True).select_related(
            'author').prefetch_related('categories')
