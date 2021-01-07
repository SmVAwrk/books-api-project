from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Books(models.Model):
    """Модель книг, которые можно забронировать"""
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey('Authors', on_delete=models.CASCADE, verbose_name='Автор', related_name='aut_books')
    categories = models.ManyToManyField('Categories', verbose_name='Категории', blank=True, related_name='cat_books')
    owner_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Кем добавлено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title


class Authors(models.Model):
    """Модель авторов книг"""
    first_name = models.CharField(verbose_name='Имя', max_length=64)
    middle_name = models.CharField(verbose_name='Отчество', max_length=64, blank=True, null=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=64)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Categories(models.Model):
    """Модель книжных категорий"""
    title = models.CharField(verbose_name='Название', max_length=255)

    def __str__(self):
        return self.title


class Libraries(models.Model):
    """Модель библиотек, в которых хранятся книги"""
    title = models.CharField(verbose_name='Название', max_length=255)
    location = models.CharField(verbose_name='Адрес', max_length=255)
    phone = models.CharField(verbose_name='Телефон', max_length=64)

    def __str__(self):
        return self.title


class BookLibraryQuantity(models.Model):
    """Модель связи определенной книги с определенной библиотекой"""
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name='Книга')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество книг')
    available = models.PositiveSmallIntegerField(verbose_name='Доступно книг')

    def __str__(self):
        return f'Связь {self.book} с {self.library}'


class UserBookSession(models.Model):
    """Модель заявки пользовтаеля на сессию с книгой"""
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    start_date = models.DateField(verbose_name='Дата начала пероида')
    end_date = models.DateField(verbose_name='Дата конца периода')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')

    def __str__(self):
        return f'Сессия {self.user} с {self.book} из {self.library}'


class UserBookOffer(models.Model):
    """Модель предложения книги пользователем"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    library = models.ForeignKey(Libraries, on_delete=models.CASCADE, verbose_name='Библиотека')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name='Книга')
    is_accepted = models.BooleanField(default=False, verbose_name='Принято')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыто')

    def __str__(self):
        return f'Предложение {self.user} книги {self.book} в {self.library}'


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
    rate = models.PositiveSmallIntegerField(choices=RATE, null=True, verbose_name='Оценка')

    def __str__(self):
        return f'Отношение {self.user} к {self.book}'


class Profile(models.Model):
    """Расширение модели User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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


