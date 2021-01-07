from rest_framework import serializers

from books.models import Books, Authors, Categories, Libraries


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'title', 'description', 'author')


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = '__all__'


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class LibrariesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libraries
        fields = ('id', 'title', 'location')
