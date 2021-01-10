from rest_framework import serializers

from books.models import Books, Authors, Categories, Libraries


class CategoriesForBooksDetailSerializer(serializers.ModelSerializer):
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


class BooksDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    author = AuthorForBooksDetailSerializer(read_only=True)
    categories = CategoriesForBooksDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Books
        fields = ('id', 'title', 'author', 'description', 'categories', 'owner')
        # exclude = ('created_at', )


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


