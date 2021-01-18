import datetime

from rest_framework import serializers

from books.models import (
    Books, Authors,
    Categories, Libraries,
    BookLibraryAvailable, UserBookSession,
    User, UserBookRelation, UserBookOffer
)


class BooksListSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.get_name')
    categories = serializers.SlugRelatedField(slug_field='title', read_only=True, many=True)
    url = serializers.HyperlinkedIdentityField(view_name='book-detail', read_only=True)

    class Meta:
        model = Books
        fields = ('title', 'author', 'categories', 'url',)


class CategoriesForBooksDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-books', read_only=True)

    class Meta:
        model = Categories
        fields = ('title', 'url')


class AuthorForBooksDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='author-books', read_only=True)
    full_name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = Authors
        fields = ('full_name', 'url')


class LibrariesForBooksDetailSerializer(serializers.ModelSerializer):
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = BookLibraryAvailable
        fields = ('library', 'available')


class BooksDetailSerializer(serializers.ModelSerializer):
    author = AuthorForBooksDetailSerializer(read_only=True)
    categories = CategoriesForBooksDetailSerializer(many=True, read_only=True)
    lib_available = LibrariesForBooksDetailSerializer(many=True, read_only=True)
    reading_now = serializers.IntegerField(read_only=True)

    class Meta:
        model = Books
        fields = ('id', 'title', 'author', 'description', 'categories', 'rating',
                  'likes', 'bookmarks', 'reading_now', 'lib_available',)


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('title', 'description', 'author', 'categories')


class AuthorsListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='author-detail', read_only=True)
    full_name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = Authors
        fields = ('full_name', 'url')


class AuthorDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='author-books', read_only=True)

    class Meta:
        model = Authors
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'description', 'url')


class AuthorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ('last_name', 'first_name', 'middle_name', 'description',)


class CategoriesListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-detail', read_only=True)

    class Meta:
        model = Categories
        fields = ('title', 'url')


class CategoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-books', read_only=True)

    class Meta:
        model = Categories
        fields = ('title', 'description', 'url')


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('title', 'description')


class LibrariesListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='library-detail', read_only=True)

    class Meta:
        model = Libraries
        fields = ('title', 'location', 'url')


class LibraryDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='library-books', read_only=True)

    class Meta:
        model = Libraries
        fields = ('id', 'title', 'location', 'phone', 'url')


class LibraryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libraries
        fields = ('title', 'location', 'phone')


class MyBooksSessionsListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='my-session-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'is_accepted', 'is_closed', 'created_at', 'url')


class MyBooksSessionDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='user.username', queryset=User.objects.all())
    library = serializers.PrimaryKeyRelatedField(source='library.title', queryset=Libraries.objects.all())
    books = serializers.SlugRelatedField(slug_field='title', queryset=Books.objects.all(), many=True)

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'books', 'start_date', 'end_date',
                  'is_accepted', 'is_closed', 'message', 'created_at')


class BooksSessionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBookSession
        fields = ('books', 'library', 'start_date', 'end_date')

    def validate(self, data):
        """Кастомная валидация полей при создании сессии"""
        books_num = len(data['books'])
        available_objects = BookLibraryAvailable.objects.filter(book__in=[book.id for book in data['books']],
                                                                library=data['library']).select_related('book',
                                                                                                        'library')
        obj_num = len(available_objects)
        if not books_num:
            raise serializers.ValidationError("Вы не выбрали ни одной книги.")
        if books_num != obj_num:
            raise serializers.ValidationError("Одной или нескольких книг нет в выбранной библиотеке")
        for available_object in available_objects:
            if not available_object.available:
                raise serializers.ValidationError(f'В данный момент {available_object.library} '
                                                  f'не имеет в наличии {available_object.book}')
        if data['start_date'] < datetime.datetime.now().date():
            raise serializers.ValidationError("Дата начала периода не может быть раньше сегодняшнего дня")
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Дата конца должна быть позже даты начала")
        return data


class UserBooksSessionsListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-session-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'is_accepted', 'is_closed', 'created_at', 'url')


class UserBooksSessionsEditSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'books', 'start_date', 'end_date',
                  'is_accepted', 'is_closed', 'message', 'created_at')

    def validate(self, data):
        """Кастомная валидация изменения сессии пользователя"""
        if self.instance.is_accepted:
            if not data['is_accepted']:
                raise serializers.ValidationError("Нельзя снять одобрение с уже одобренной сессии.")
        if self.instance.is_closed:
            raise serializers.ValidationError("Сессия закрыта. Изменение невозможно.")
        return data


class BooksLibrariesAvailableListSerializer(serializers.HyperlinkedModelSerializer):
    book = serializers.ReadOnlyField(source='book.title')
    library = serializers.ReadOnlyField(source='library.title')
    url = serializers.HyperlinkedIdentityField(view_name='available-detail', read_only=True)

    class Meta:
        model = BookLibraryAvailable
        fields = ('book', 'library', 'available', 'url')


class BooksLibrariesAvailableDetailSerializer(serializers.ModelSerializer):
    book = serializers.ReadOnlyField(source='book.title')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = BookLibraryAvailable
        fields = ('id', 'book', 'library', 'available')


class BooksLibrariesAvailableEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLibraryAvailable
        fields = ('id', 'book', 'library', 'available')


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        exclude = ('user', 'id')


class MyBooksOffersListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='my-offer-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = UserBookOffer
        fields = ('user', 'library', 'is_accepted', 'is_closed', 'created_at', 'url')


class MyBooksOfferDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='user.username', queryset=User.objects.all())
    library = serializers.PrimaryKeyRelatedField(source='library.title', queryset=Libraries.objects.all())

    class Meta:
        model = UserBookOffer
        fields = ('user', 'library', 'quantity', 'books_description',
                  'is_accepted', 'is_closed', 'message', 'created_at')


class MyBooksOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookOffer
        fields = ('library', 'quantity', 'books_description')


class UserBooksOffersListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-offer-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = UserBookOffer
        fields = ('user', 'library', 'is_accepted', 'is_closed', 'created_at', 'url')


class UserBooksOfferEditSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserBookOffer
        fields = ('user', 'library', 'quantity', 'books_description',
                  'is_accepted', 'is_closed', 'message', 'created_at')

    def validate(self, data):
        """Кастомная валидация изменения сессии пользователя"""
        if self.instance.is_accepted:
            if not data['is_accepted']:
                raise serializers.ValidationError("Нельзя снять одобрение с уже одобренной заявки.")
        if self.instance.is_closed:
            raise serializers.ValidationError("Заявка закрыта. Изменение невозможно.")
        return data
