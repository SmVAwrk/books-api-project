from django.db.models import Avg, Count
from django_filters.rest_framework import FilterSet, DateRangeFilter, DateFromToRangeFilter, BooleanFilter, \
    MultipleChoiceFilter, ChoiceFilter, ModelMultipleChoiceFilter, ModelChoiceFilter

from books.models import UserBookSession, UserBookOffer, Books, Categories, Authors, BookLibraryAvailable, Libraries, \
    UserBookRelation


class UserBookOfferFilter(FilterSet):
    created_at = DateFromToRangeFilter()
    is_accepted = BooleanFilter()
    is_closed = BooleanFilter()

    class Meta:
        model = UserBookOffer
        fields = ['created_at', 'is_accepted', 'is_closed']


class UserBookSessionFilter(FilterSet):
    created_at = DateFromToRangeFilter()
    is_accepted = BooleanFilter()
    is_closed = BooleanFilter()

    class Meta:
        model = UserBookSession
        fields = ['created_at', 'is_accepted', 'is_closed']


class BooksListFilter(FilterSet):
    categories = ModelMultipleChoiceFilter(queryset=Categories.objects.all(), conjoined=True)
    author = ModelChoiceFilter(queryset=Authors.objects.all())
    lib_available__library = ModelChoiceFilter(queryset=Libraries.objects.all())

    class Meta:
        model = Books
        fields = ['categories', 'author', 'lib_available__library']


def get_rating(book):
    book.rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.save()


def get_likes(book):
    book.likes = UserBookRelation.objects.filter(book=book, like=True).select_related('user').count()
    book.save()


def get_bookmarks(book):
    book.bookmarks = UserBookRelation.objects.filter(book=book, in_bookmarks=True).select_related('user').count()
    book.save()


