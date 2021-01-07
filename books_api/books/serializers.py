from rest_framework import serializers

from books.models import Books, Authors, Categories, Libraries


class BooksListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'title', 'author')


class BooksDetailSerializer(serializers.ModelSerializer):
    owner_user = serializers.ReadOnlyField(source='owner_user.username')
    author = serializers.CharField(source='author.last_name')
    # categories = serializers.ListField()

    class Meta:
        model = Books
        fields = '__all__'


class BooksCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'title', 'description', 'author', 'categories')


class AuthorsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = '__all__'


class CategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class LibrariesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libraries
        fields = ('id', 'title', 'location')
