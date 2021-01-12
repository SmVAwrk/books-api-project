import datetime

from rest_framework import serializers

from books.models import Books, Authors, Categories, Libraries, BookLibraryAvailable, UserBookSession, User


class CategoriesForBooksDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-detail-books', read_only=True)

    class Meta:
        model = Categories
        fields = ('title', 'url')


class BooksListSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.CharField(source='author.get_name')
    categories = serializers.SlugRelatedField(slug_field='title', read_only=True, many=True)
    url = serializers.HyperlinkedIdentityField(view_name='book-detail', read_only=True)

    class Meta:
        model = Books
        fields = ('title', 'author', 'categories', 'url',)


class AuthorForBooksDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='author-detail-books', read_only=True)
    full_name = serializers.ReadOnlyField(source='__str__')

    class Meta:
        model = Authors
        fields = ('full_name', 'url')


class BookLibrarySerializer(serializers.HyperlinkedModelSerializer):
    library = serializers.ReadOnlyField(source='library.title')
    # url = serializers.HyperlinkedIdentityField(view_name='create-session-library', read_only=True)

    class Meta:
        model = BookLibraryAvailable
        fields = ('library', 'available')


class BooksDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    author = AuthorForBooksDetailSerializer(read_only=True)
    categories = CategoriesForBooksDetailSerializer(many=True, read_only=True)
    lib_available = BookLibrarySerializer(many=True, read_only=True)
    # create_session_url = serializers.HyperlinkedIdentityField(view_name='create-session', read_only=True)

    class Meta:
        model = Books
        fields = ('id', 'title', 'author', 'description', 'categories', 'owner', 'lib_available')


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
    owner = serializers.ReadOnlyField(source='owner.username')
    url = serializers.HyperlinkedIdentityField(view_name='author-detail-books', read_only=True)

    class Meta:
        model = Authors
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'description', 'owner', 'url')


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
    url = serializers.HyperlinkedIdentityField(view_name='category-detail-books', read_only=True)

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
    url = serializers.HyperlinkedIdentityField(view_name='library-detail-books', read_only=True)

    class Meta:
        model = Libraries
        fields = ('id', 'title', 'location', 'phone', 'url')


class BookSessionCreateFromLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookSession
        fields = ('books', 'start_date', 'end_date')


class BookSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookSession
        fields = ('books', 'library', 'start_date', 'end_date')

    def validate(self, data):
        """Кастомная валидация полей при создании сессии"""
        books_num = len(data['books'])
        available_objects = BookLibraryAvailable.objects.filter(book__in=[book.id for book in data['books']],
                                                                library=data['library']).select_related('book', 'library')
        obj_num = len(available_objects)
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


class BookSessionEditSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(source='user.username', queryset=User.objects.all())
    library = serializers.PrimaryKeyRelatedField(source='user.username', queryset=Libraries.objects.all())
    books = serializers.SlugRelatedField(slug_field='title', queryset=Books.objects.all(), many=True)

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'books',  'start_date', 'end_date', 'is_accepted', 'is_closed')


class BooksSessionsListSerializer(serializers.ModelSerializer):  # !!!Работает только с ModelSerializer!!!
    url = serializers.HyperlinkedIdentityField(view_name='session-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    library = serializers.ReadOnlyField(source='library.title')

    class Meta:
        model = UserBookSession
        fields = ('user', 'library', 'is_accepted', 'url')


