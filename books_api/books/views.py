from django.db.models import Count, Case, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from books.models import Books, Authors, Categories, Libraries, UserBookSession, UserBookRelation
from books.serializers import *
from books.services import UserBookOfferFilter, UserBookSessionFilter, BooksListFilter


# @api_view(['GET'])
# def api_root(request, format=None):
#     """Представление для корня api"""
#     return Response({
#         'books': reverse('books-list', request=request, format=format),
#         'authors': reverse('authors', request=request, format=format),
#         'categories': reverse('categories', request=request, format=format),
#         'libraries': reverse('libraries', request=request, format=format),
#         'create-session': reverse('create-session', request=request, format=format),
#         'sessions(admin)': reverse('sessions', request=request, format=format),
#         'my-sessions': reverse('my-sessions', request=request, format=format),
#     })


class BooksViewSet(viewsets.ModelViewSet):
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title']
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
        books_by_author = Books.objects.filter(author=self.get_object()).select_related('author').prefetch_related(
            'categories')
        page = self.paginate_queryset(books_by_author)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books_by_author, many=True)
        return Response(serializer.data)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title']

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
        books_by_category = Books.objects.filter(categories=self.get_object()).select_related(
            'author').prefetch_related('categories')
        page = self.paginate_queryset(books_by_category)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books_by_category, many=True)
        return Response(serializer.data)


class LibrariesViewSet(viewsets.ModelViewSet):
    queryset = Libraries.objects.all()
    filter_backends = [SearchFilter, ]
    search_fields = ['title']

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
            return (permissions.AllowAny(),)
        else:
            return (permissions.IsAdminUser(),)

    @action(
        detail=True,
        url_name='books',
        url_path='books'
    )
    def get_books(self, request, pk=None):
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
    permission_classes = (permissions.IsAuthenticated,)
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
    queryset = UserBookSession.objects.all().select_related('user', 'library').prefetch_related('books')
    permission_classes = (permissions.IsAdminUser,)
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
    queryset = BookLibraryAvailable.objects.all().select_related('book', 'library')
    permission_classes = (permissions.IsAdminUser,)
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
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj


class MyOffersViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
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
    queryset = UserBookOffer.objects.all().select_related('user', 'library')
    permission_classes = (permissions.IsAdminUser,)
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
    permission_classes = (permissions.IsAuthenticated,)
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
