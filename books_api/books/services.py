from django.db.models import Avg, Count
from django_filters.rest_framework import (
    FilterSet, DateFromToRangeFilter, BooleanFilter,
    ModelMultipleChoiceFilter, ModelChoiceFilter
)
from books.models import UserBookSession, UserBookOffer, Books, Categories, Authors, Libraries, UserBookRelation


class UserBookOfferFilter(FilterSet):
    """
    Кастомный фильтр для UserOffersViewSet:
    выбор интервала даты создания,
    выбор принятых,
    выбор закрытых
    """
    created_at = DateFromToRangeFilter()
    is_accepted = BooleanFilter()
    is_closed = BooleanFilter()

    class Meta:
        model = UserBookOffer
        fields = ['created_at', 'is_accepted', 'is_closed']


class UserBookSessionFilter(FilterSet):
    """
    Кастомный фильтр для UserSessionsViewSet:
    выбор интервала даты создания,
    выбор принятых,
    выбор закрытых
    """
    created_at = DateFromToRangeFilter()
    is_accepted = BooleanFilter()
    is_closed = BooleanFilter()

    class Meta:
        model = UserBookSession
        fields = ['created_at', 'is_accepted', 'is_closed']


class BooksListFilter(FilterSet):
    """
    Кастомный фильтр для BooksViewSet:
    выбор категорий,
    выбор автора,
    выбор библиотеки
    """
    categories = ModelMultipleChoiceFilter(queryset=Categories.objects.all())
    author = ModelChoiceFilter(queryset=Authors.objects.all())
    lib_available__library = ModelChoiceFilter(queryset=Libraries.objects.all())

    class Meta:
        model = Books
        fields = ['categories', 'author', 'lib_available__library']


def set_rating(book):
    """
    Функция для подсчёта рейтинга книги,
    в качестве аргумента принимает экземпляр книги
    """
    book.rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.save()


def set_likes(book):
    """
    Функция для подсчёта лайков книги,
    в качестве аргумента принимает экземпляр книги
    """
    book.likes = UserBookRelation.objects.filter(book=book, like=True).select_related('user').count()
    book.save()


def set_bookmarks(book):
    """
    Функция для подсчёта закладок книги,
    в качестве аргумента принимает экземпляр книги
    """
    book.bookmarks = UserBookRelation.objects.filter(book=book, in_bookmarks=True).select_related('user').count()
    book.save()


def set_book_values(serializer, created):
    """
    Функция для обновления полей рейтинга, лайков и закладок книги при создании или изменении отношения,
    в качестве аргументов принимает сериализатор и bool-значение создания отношения
    """
    functions_dict = {
        'rate': set_rating,
        'like': set_likes,
        'in_bookmarks': set_bookmarks
    }
    if created:
        for field in functions_dict:
            function = functions_dict[field]
            function(serializer.instance.book)
    else:
        for field in serializer.validated_data:
            function = functions_dict.get(field)
            if not function:
                continue
            function(serializer.instance.book)
