from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Books(models.Model):
    """Модель книг, которые можно забронировать"""
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey('Authors', on_delete=models.CASCADE, verbose_name='Автор', related_name='aut_books')
    categories = models.ManyToManyField('Categories', verbose_name='Категории', blank=True, related_name='cat_books')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Authors(models.Model):
    """Модель авторов книг"""
    first_name = models.CharField(verbose_name='Имя', max_length=64)
    middle_name = models.CharField(verbose_name='Отчество', max_length=64, blank=True, null=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=64)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    class Meta:
        ordering = ['last_name']

    def get_name(self):
        name = (f'{self.first_name[0]}. {self.middle_name[0]}. {self.last_name}'
                if self.middle_name else f'{self.first_name[0]}. {self.last_name}')
        return name

    def __str__(self):
        full_name = (f'{self.first_name} {self.middle_name} {self.last_name}'
                     if self.middle_name else f'{self.first_name} {self.last_name}')
        return full_name


class Categories(models.Model):
    """Модель книжных категорий"""
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return self.title


class Libraries(models.Model):
    """Модель библиотек, в которых хранятся книги"""
    title = models.CharField(verbose_name='Название', max_length=255)
    location = models.CharField(verbose_name='Адрес', max_length=255)
    phone = models.CharField(verbose_name='Телефон', max_length=64)

    def __str__(self):
        return self.title


class BookLibraryAvailable(models.Model):
    """Модель связи определенной книги с определенной библиотекой"""
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name='Книга', related_name='lib_available')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE,
                                verbose_name='Библиотека', related_name='book_available')
    available = models.BooleanField(verbose_name='В наличии')

    class Meta:
        ordering = ('book', 'library')
        unique_together = ('book', 'library')

    def __str__(self):
        return f'Связь {self.book} с {self.library}'


class UserBookSession(models.Model):
    """Модель заявки пользовтаеля на сессию с книгой"""
    books = models.ManyToManyField(Books, verbose_name='Книги', blank=True, related_name='session_books')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    start_date = models.DateField(verbose_name='Дата, когда заберут книги')
    end_date = models.DateField(verbose_name='Дата, когда вернут книги')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')

    class Meta:
        ordering = ('is_closed', 'is_accepted', 'user', 'library')

    def __str__(self):
        return f'Сессия {self.user} в {self.library}'

    # def save(self, *args, **kwargs):
    #     old_accepted = self.is_accepted
    #     old_closed = self.is_closed
    #     super().save(*args, **kwargs)
    #     new_accepted = self.is_accepted
    #     new_closed = self.is_closed
    #     if old_accepted != new_accepted:
    #         book_library_relation = BookLibraryQuantity.objects.get(book=self.book,
    #                                                                 library=self.library)
    #         book_library_relation.available = F('available') - 1
    #         book_library_relation.save()
    #         book_library_relation.refresh_from_db()
    #     if old_closed != new_closed:
    #         book_library_relation = BookLibraryQuantity.objects.get(book=self.book,
    #                                                                 library=self.library)
    #         book_library_relation.available = F('available') + 1
    #         book_library_relation.save()
    #         book_library_relation.refresh_from_db()


class UserBookOffer(models.Model):
    """Модель предложения книг пользователем"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    quantity = models.PositiveSmallIntegerField(verbose_name='Кол-во книг')
    books_description = models.TextField(verbose_name='Описание книг')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')

    def __str__(self):
        return f'Предложение {self.user} книг в {self.library}'


class UserBookRelation(models.Model):
    """Модель отношения пользователя и книги"""
    RATE = (
        (1, 'Плохо'),
        (2, 'Так себе'),
        (3, 'Нормально'),
        (4, 'Хорошо'),
        (5, 'Отлично')
    )
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    like = models.BooleanField(default=False, verbose_name='Мне нравится')
    in_bookmarks = models.BooleanField(default=False, verbose_name='В закладки')
    rate = models.PositiveSmallIntegerField(choices=RATE, null=True, verbose_name='Оценка')

    def __str__(self):
        return f'Отношение {self.user} к {self.book}'


class Profile(models.Model):
    """Расширение модели User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='prof')
    phone_number = models.CharField(verbose_name='Телефон', max_length=64, blank=True)
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    books_donated = models.PositiveIntegerField(verbose_name='Отдано книг', default=0)

    def __str__(self):
        return f'Профиль {self.user}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


