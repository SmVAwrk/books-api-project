from rest_framework import serializers

from books.models import Books, Authors, Categories, Libraries


class BooksListSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.CharField(source='author.get_name')
    url = serializers.HyperlinkedIdentityField(view_name='book-detail', read_only=True)

    class Meta:
        model = Books
        fields = ('title', 'author', 'url',)


class BooksDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    author = serializers.PrimaryKeyRelatedField(label='Автор', queryset=Authors.objects.all(), source='author.__str__')
    # categories = serializers.ManyRelatedField(child_relation=Categories.objects.book.all())

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
