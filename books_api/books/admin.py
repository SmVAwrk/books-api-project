from django.contrib import admin
from books.models import (
    Books, Authors, Categories,
    Libraries, BookLibraryAvailable, UserBookSession,
    UserBookRelation, UserBookOffer
)

admin.site.register(Books)
admin.site.register(Authors)
admin.site.register(Categories)
admin.site.register(Libraries)
admin.site.register(BookLibraryAvailable)
admin.site.register(UserBookSession)
admin.site.register(UserBookRelation)
admin.site.register(UserBookOffer)
