from django_filters.rest_framework import FilterSet, DateRangeFilter, DateFromToRangeFilter, BooleanFilter

from books.models import UserBookSession, UserBookOffer


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
