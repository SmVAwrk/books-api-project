from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Books(models.Model):
    """Модель книг, доступных в в библиотеке"""
    title = models.CharField(verbose_name='Название', max_length=255, unique=True)
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey('Authors', on_delete=models.CASCADE, verbose_name='Автор', related_name='aut_books')
    categories = models.ManyToManyField('Categories', verbose_name='Категории', blank=True, related_name='cat_books')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, default=None, verbose_name='Рейтинг')
    likes = models.PositiveIntegerField(default=0, verbose_name='Мне нравится')
    bookmarks = models.PositiveIntegerField(default=0, verbose_name='В закладках')

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

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Libraries(models.Model):
    """Модель библиотек, в которых хранятся книги"""
    title = models.CharField(verbose_name='Название', max_length=255)
    location = models.CharField(verbose_name='Адрес', max_length=255)
    phone = models.CharField(verbose_name='Телефон', max_length=64)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class BookLibraryAvailable(models.Model):
    """Модель наличия и доступности определенной книги в определенной библиотекой"""
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
    """Модель заявки пользователя на сессию с книгами"""
    books = models.ManyToManyField(Books, verbose_name='Книги', blank=True, related_name='session_books')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    start_date = models.DateField(verbose_name='Дата, когда заберут книги')
    end_date = models.DateField(verbose_name='Дата, когда вернут книги')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')
    message = models.TextField(verbose_name='Комментарий', default='-')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ('-created_at', 'is_closed', 'is_accepted', 'user', 'library')

    def __str__(self):
        return f'Сессия {self.user} в {self.library}'


class UserBookOffer(models.Model):
    """Модель предложения книг в определенную библиотеку"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    quantity = models.PositiveSmallIntegerField(verbose_name='Кол-во книг')
    books_description = models.TextField(verbose_name='Описание книг')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')
    message = models.TextField(verbose_name='Комментарий', default='-')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Предложение {self.user} книг в {self.library}'

    class Meta:
        ordering = ('-created_at', 'is_closed', 'is_accepted', 'user', 'library')


class UserBookRelation(models.Model):
    """Модель отношения пользователя к книги"""
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
    rate = models.PositiveSmallIntegerField(choices=RATE, blank=True, null=True, verbose_name='Оценка')

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f'Отношение {self.user} к {self.book}'
