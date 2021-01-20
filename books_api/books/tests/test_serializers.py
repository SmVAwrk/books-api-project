from django.db.models import Case, When, Count
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from books.serializers import *


class BooksListSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.author_2 = Authors.objects.create(
            first_name='Test',
            last_name='Author 2'
        )
        self.category_1 = Categories.objects.create(title='Test category 1')
        self.category_2 = Categories.objects.create(title='Test category 2')
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_1.categories.add(self.category_1)

        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_2,
        )
        self.book_2.categories.add(self.category_2)

    def test_ok(self):
        expected_data = [
            {
                'title': 'Test book 1',
                'author': 'T. Author 1',
                'categories': [
                    'Test category 1',
                ],
                'url': f'/api/v1/books/{self.book_1.id}/'
            },
            {
                'title': 'Test book 2',
                'author': 'T. Author 2',
                'categories': [
                    'Test category 2',
                ],
                'url': f'/api/v1/books/{self.book_2.id}/'
            },
        ]
        data = BooksListSerializer([self.book_1, self.book_2], many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class CategoriesForBooksDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.category_1 = Categories.objects.create(title='Test category 1')
        self.category_2 = Categories.objects.create(title='Test category 2')

    def test_ok(self):
        expected_data = [
            {
                'title': 'Test category 1',
                'url': f'/api/v1/categories/{self.category_1.id}/books/'
            },
            {
                'title': 'Test category 2',
                'url': f'/api/v1/categories/{self.category_2.id}/books/'
            },
        ]
        data = CategoriesForBooksDetailSerializer([self.category_1, self.category_2],
                                                  many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class AuthorForBooksDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.author_2 = Authors.objects.create(
            first_name='Test',
            middle_name='Mid',
            last_name='Author 2'
        )

    def test_ok(self):
        expected_data = [
            {
                'full_name': 'Test Author 1',
                'url': f'/api/v1/authors/{self.author_1.id}/books/'
            },
            {
                'full_name': 'Test Mid Author 2',
                'url': f'/api/v1/authors/{self.author_2.id}/books/'
            },
        ]
        data = AuthorForBooksDetailSerializer([self.author_1, self.author_2], many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class LibrariesForBooksDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-222-222-22-22'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.book_library_2 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_2,
            available=False
        )

    def test_ok(self):
        expected_data = [
            {
                'library': 'Test Library 1',
                'available': True
            },
            {
                'library': 'Test Library 2',
                'available': False
            },
        ]
        data = LibrariesForBooksDetailSerializer([self.book_library_1, self.book_library_2], many=True).data
        self.assertEqual(expected_data, data, msg=data)


class BooksDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.category_1 = Categories.objects.create(title='Test category 1')
        self.category_2 = Categories.objects.create(title='Test category 2')
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_1.categories.add(self.category_1, self.category_2)
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-222-222-22-22'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.book_library_2 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_2,
            available=False
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)

        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end,
                                                        is_accepted=True, is_closed=False)
        self.session_1.books.add(self.book_1)
        self.session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end,
                                                        is_accepted=False, is_closed=False)
        self.session_2.books.add(self.book_1)
        self.session_3 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end,
                                                        is_accepted=True, is_closed=True)
        self.session_3.books.add(self.book_1)

    def test_ok(self):
        expected_data = {
            'id': self.book_1.id,
            'title': 'Test book 1',
            'author': {
                'full_name': 'Test Author 1',
                'url': f'/api/v1/authors/{self.author_1.id}/books/'
            },
            'description': 'Test description 1',
            'categories': [
                {
                    'title': 'Test category 1',
                    'url': f'/api/v1/categories/{self.category_1.id}/books/'
                },
                {
                    'title': 'Test category 2',
                    'url': f'/api/v1/categories/{self.category_2.id}/books/'
                },
            ],
            'rating': None,
            'likes': 0,
            'bookmarks': 0,
            'lib_available': [
                {
                    'library': 'Test Library 1',
                    'available': True
                },
                {
                    'library': 'Test Library 2',
                    'available': False
                },
            ]
        }
        data = BooksDetailSerializer(self.book_1, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)

    def test_annotated_reading_now(self):
        books = Books.objects.all().annotate(
            reading_now=Count(Case(When(session_books__is_accepted=True,
                                        session_books__is_closed=False,
                                        then=1)))
        )
        data = BooksDetailSerializer(books, many=True, context={'request': None}).data
        self.assertEqual(1, data[0]['reading_now'], msg=data)


class BookCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.category_1 = Categories.objects.create(title='Test category 1')
        self.category_2 = Categories.objects.create(title='Test category 2')
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_1.categories.add(self.category_1, self.category_2)

    def test_ok(self):
        expected_data = {
            'title': 'Test book 1',
            'author': self.author_1.id,
            'description': 'Test description 1',
            'categories': [
                self.category_1.id,
                self.category_2.id
            ]
        }
        data = BookCreateSerializer(self.book_1).data
        self.assertEqual(expected_data, data, msg=data)


class AuthorsListSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.author_2 = Authors.objects.create(
            first_name='Test',
            middle_name='Mid',
            last_name='Author 2'
        )

    def test_ok(self):
        expected_data = [
            {
                'full_name': 'Test Author 1',
                'url': f'/api/v1/authors/{self.author_1.id}/'
            },
            {
                'full_name': 'Test Mid Author 2',
                'url': f'/api/v1/authors/{self.author_2.id}/'
            }
        ]
        data = AuthorsListSerializer([self.author_1, self.author_2], many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class AuthorDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            middle_name='Mid',
            last_name='Author 1',
            description='Test description'
        )

    def test_ok(self):
        expected_data = {
            'id': self.author_1.id,
            'last_name': 'Author 1',
            'first_name': 'Test',
            'middle_name': 'Mid',
            'description': 'Test description',
            'url': f'/api/v1/authors/{self.author_1.id}/books/'
        }
        data = AuthorDetailSerializer(self.author_1, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class AuthorCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            middle_name='Mid',
            last_name='Author 1',
            description='Test description'
        )

    def test_ok(self):
        expected_data = {
            'last_name': 'Author 1',
            'first_name': 'Test',
            'middle_name': 'Mid',
            'description': 'Test description',
        }
        data = AuthorCreateSerializer(self.author_1).data
        self.assertEqual(expected_data, data, msg=data)


class CategoriesListSerializerTestCase(TestCase):

    def setUp(self):
        self.category_1 = Categories.objects.create(
            title='Test category 1',
            description='Test description'
        )
        self.category_2 = Categories.objects.create(
            title='Test category 2',
            description='Test description'
        )

    def test_ok(self):
        expected_data = [
            {
                'title': 'Test category 1',
                'url': f'/api/v1/categories/{self.category_1.id}/'
            },
            {
                'title': 'Test category 2',
                'url': f'/api/v1/categories/{self.category_2.id}/'
            }
        ]
        data = CategoriesListSerializer([self.category_1, self.category_2], many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class CategoryDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.category_1 = Categories.objects.create(
            title='Test category 1',
            description='Test description'
        )

    def test_ok(self):
        expected_data = {
            'title': 'Test category 1',
            'description': 'Test description',
            'url': f'/api/v1/categories/{self.category_1.id}/books/'
        }
        data = CategoryDetailSerializer(self.category_1, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class CategoryCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.category_1 = Categories.objects.create(
            title='Test category 1',
            description='Test description'
        )

    def test_ok(self):
        expected_data = {
            'title': 'Test category 1',
            'description': 'Test description',
        }
        data = CategoryCreateSerializer(self.category_1).data
        self.assertEqual(expected_data, data, msg=data)


class LibrariesListSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-222-222-22-22'
        )

    def test_ok(self):
        expected_data = [
            {
                'title': 'Test Library 1',
                'location': 'Test location 1',
                'url': f'/api/v1/libraries/{self.library_1.id}/'
            },
            {
                'title': 'Test Library 2',
                'location': 'Test location 2',
                'url': f'/api/v1/libraries/{self.library_2.id}/'
            }
        ]
        data = LibrariesListSerializer([self.library_1, self.library_2], many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class LibraryDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )

    def test_ok(self):
        expected_data = {
            'id': self.library_1.id,
            'title': 'Test Library 1',
            'location': 'Test location 1',
            'phone': '1-111-111-11-11',
            'url': f'/api/v1/libraries/{self.library_1.id}/books/'
        }
        data = LibraryDetailSerializer(self.library_1, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class LibraryCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )

    def test_ok(self):
        expected_data = {
            'title': 'Test Library 1',
            'location': 'Test location 1',
            'phone': '1-111-111-11-11',
        }
        data = LibraryCreateSerializer(self.library_1).data
        self.assertEqual(expected_data, data, msg=data)


class MyBooksSessionsListSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.book_library_2 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_2,
            available=True
        )

        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)
        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_2,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_1.books.add(self.book_1)
        self.session_2.books.add(self.book_2)

    def test_ok(self):
        expected_data = [
            {
                'user': 'User1',
                'library': 'Test Library 1',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.session_1.created_at),
                'url': f'/api/v1/my-sessions/{self.session_1.id}/'
            },
            {
                'user': 'User1',
                'library': 'Test Library 2',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.session_1.created_at),
                'url': f'/api/v1/my-sessions/{self.session_2.id}/'
            }
        ]
        data = MyBooksSessionsListSerializer([self.session_1, self.session_2],
                                             many=True, context={'request': None}).data
        for session in data:
            session['created_at'] = str(self.session_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class MyBooksSessionDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)

        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_1.books.add(self.book_1, self.book_2)

    def test_ok(self):
        expected_data = {
            'user': 'User1',
            'library': 'Test Library 1',
            'books': [
                'Test book 2',
                'Test book 1'
            ],
            'start_date': str(self.test_start),
            'end_date': str(self.test_end),
            'is_accepted': False,
            'is_closed': False,
            'message': '-',
            'created_at': str(self.session_1.created_at)
        }
        data = MyBooksSessionDetailSerializer(self.session_1).data
        data['created_at'] = str(self.session_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class BooksSessionCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.user_1 = User.objects.create(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)

        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_1.books.add(self.book_1)

    def test_ok(self):
        expected_data = {
            'books': [
                self.book_1.id
            ],
            'library': self.library_1.id,
            'start_date': str(self.test_start),
            'end_date': str(self.test_end),
        }
        data = BooksSessionCreateSerializer(self.session_1).data
        self.assertEqual(expected_data, data, msg=data)

    def test_validation_valid_data(self):
        valid_data = {
            'books': [
                self.book_1,
            ],
            'library': self.library_1,
            'start_date': self.test_start,
            'end_date': self.test_end,
        }
        data = BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=valid_data)
        self.assertEqual(valid_data, data)

    def test_validation_without_books(self):
        not_valid_data = {
            'books': [],
            'library': self.library_1,
            'start_date': self.test_start,
            'end_date': self.test_end
        }
        with self.assertRaises(ValidationError):
            BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=not_valid_data)

    def test_validation_without_book_library_relation(self):
        not_valid_data = {
            'books': [
                self.book_1,
                self.book_2
            ],
            'library': self.library_1,
            'start_date': self.test_start,
            'end_date': self.test_end
        }
        with self.assertRaises(ValidationError):
            BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=not_valid_data)

    def test_validation_book_not_available(self):
        BookLibraryAvailable.objects.create(
            book=self.book_2,
            library=self.library_1,
            available=False
        )
        not_valid_data = {
            'books': [
                self.book_1,
                self.book_2
            ],
            'library': self.library_1,
            'start_date': self.test_start,
            'end_date': self.test_end
        }
        with self.assertRaises(ValidationError):
            BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=not_valid_data)

    def test_validation_start_date_yesterday(self):
        test_start = datetime.datetime.now().date() - datetime.timedelta(days=1)
        not_valid_data = {
            'books': [
                self.book_1,
            ],
            'library': self.library_1,
            'start_date': test_start,
            'end_date': self.test_end
        }
        with self.assertRaises(ValidationError):
            BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=not_valid_data)

    def test_validation_end_date_yesterday(self):
        test_end = datetime.datetime.now().date() - datetime.timedelta(days=1)
        not_valid_data = {
            'books': [
                self.book_1,
            ],
            'library': self.library_1,
            'start_date': self.test_start,
            'end_date': test_end
        }
        with self.assertRaises(ValidationError):
            BooksSessionCreateSerializer.validate(self=BooksSessionCreateSerializer(), data=not_valid_data)


class UserBooksSessionsListSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.book_library_2 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_2,
            available=True
        )

        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)
        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_2,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_1.books.add(self.book_1)
        self.session_2.books.add(self.book_2)

    def test_ok(self):
        expected_data = [
            {
                'user': 'User1',
                'library': 'Test Library 1',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.session_1.created_at),
                'url': f'/api/v1/user-sessions/{self.session_1.id}/'
            },
            {
                'user': 'User1',
                'library': 'Test Library 2',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.session_1.created_at),
                'url': f'/api/v1/user-sessions/{self.session_2.id}/'
            }
        ]
        data = UserBooksSessionsListSerializer([self.session_1, self.session_2],
                                               many=True, context={'request': None}).data
        for session in data:
            session['created_at'] = str(self.session_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class UserBooksSessionsEditSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)

        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_1.books.add(self.book_1, self.book_2)

    def test_ok(self):
        expected_data = {
            'user': 'User1',
            'library': self.library_1.id,
            'books': [
                self.book_2.id,
                self.book_1.id
            ],
            'start_date': str(self.test_start),
            'end_date': str(self.test_end),
            'is_accepted': False,
            'is_closed': False,
            'message': '-',
            'created_at': str(self.session_1.created_at)
        }
        data = UserBooksSessionsEditSerializer(self.session_1).data
        data['created_at'] = str(self.session_1.created_at)
        self.assertEqual(expected_data, data, msg=data)

    def test_validate_valid_data(self):
        session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                   start_date=self.test_start,
                                                   end_date=self.test_end)
        session_2.books.add(self.book_1)
        valid_data = {
            'is_accepted': True,
            'message': 'Test message',
        }
        data = UserBooksSessionsEditSerializer.validate(self=UserBooksSessionsEditSerializer(instance=session_2),
                                                        data=valid_data)
        self.assertEqual(valid_data, data)

    def test_validate_cancel_accept(self):
        session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                   start_date=self.test_start,
                                                   end_date=self.test_end, is_accepted=True)
        session_2.books.add(self.book_1)
        not_valid_data = {
            'is_accepted': False
        }
        with self.assertRaises(ValidationError):
            UserBooksSessionsEditSerializer.validate(self=UserBooksSessionsEditSerializer(instance=session_2),
                                                     data=not_valid_data)

    def test_validate_change_closed(self):
        session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                   start_date=self.test_start,
                                                   end_date=self.test_end, is_closed=True)
        session_2.books.add(self.book_1)
        not_valid_data = {
            'is_closed': False
        }
        with self.assertRaises(ValidationError):
            UserBooksSessionsEditSerializer.validate(self=UserBooksSessionsEditSerializer(instance=session_2),
                                                     data=not_valid_data)


class BooksLibrariesAvailableListSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )
        self.book_library_2 = BookLibraryAvailable.objects.create(
            book=self.book_2,
            library=self.library_2,
            available=False
        )

    def test_ok(self):
        expected_data = [
            {
                'book': 'Test book 1',
                'library': 'Test Library 1',
                'available': True,
                'url': f'/api/v1/available/{self.book_library_1.id}/'
            },
            {
                'book': 'Test book 2',
                'library': 'Test Library 2',
                'available': False,
                'url': f'/api/v1/available/{self.book_library_2.id}/'
            }
        ]
        data = BooksLibrariesAvailableListSerializer([self.book_library_1, self.book_library_2],
                                                     many=True, context={'request': None}).data
        self.assertEqual(expected_data, data, msg=data)


class BooksLibrariesAvailableDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )

    def test_ok(self):
        expected_data = {
            'id': self.book_library_1.id,
            'book': 'Test book 1',
            'library': 'Test Library 1',
            'available': True,
        }
        data = BooksLibrariesAvailableDetailSerializer(self.book_library_1).data
        self.assertEqual(expected_data, data, msg=data)


class BooksLibrariesAvailableEditSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.book_library_1 = BookLibraryAvailable.objects.create(
            book=self.book_1,
            library=self.library_1,
            available=True
        )

    def test_ok(self):
        expected_data = {
            'id': self.book_library_1.id,
            'book': self.book_1.id,
            'library': self.library_1.id,
            'available': True,
        }
        data = BooksLibrariesAvailableEditSerializer(self.book_library_1).data
        self.assertEqual(expected_data, data, msg=data)


class UserBookRelationSerializerTestCase(TestCase):

    def setUp(self):
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.book_relation_1 = UserBookRelation(user=self.user_1, book=self.book_1, like=True, rate=5)

    def test_ok(self):
        expected_data = {
            'like': True,
            'in_bookmarks': False,
            'rate': 5,
            'book': self.book_1.id
        }
        data = UserBookRelationSerializer(self.book_relation_1).data
        self.assertEqual(expected_data, data, msg=data)


class MyBooksOffersListSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-111-111-11-11'
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Testdis1')
        self.offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_2,
                                                    quantity=2, books_description='Testdis2')

    def test_ok(self):
        expected_data = [
            {
                'user': 'User1',
                'library': 'Test Library 1',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.offer_1.created_at),
                'url': f'/api/v1/my-offers/{self.offer_1.id}/'
            },
            {
                'user': 'User1',
                'library': 'Test Library 2',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.offer_1.created_at),
                'url': f'/api/v1/my-offers/{self.offer_2.id}/'
            }
        ]
        data = MyBooksOffersListSerializer([self.offer_1, self.offer_2],
                                           many=True, context={'request': None}).data
        for session in data:
            session['created_at'] = str(self.offer_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class MyBooksOfferDetailSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Testdis1')

    def test_ok(self):
        expected_data = {
            'user': 'User1',
            'library': 'Test Library 1',
            'quantity': 1,
            'books_description': 'Testdis1',
            'is_accepted': False,
            'is_closed': False,
            'message': '-',
            'created_at': str(self.offer_1.created_at)
        }
        data = MyBooksOfferDetailSerializer(self.offer_1).data
        data['created_at'] = str(self.offer_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class MyBooksOfferCreateSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Testdis1')

    def test_ok(self):
        expected_data = {
            'library': self.library_1.id,
            'quantity': 1,
            'books_description': 'Testdis1',
        }
        data = MyBooksOfferCreateSerializer(self.offer_1).data
        self.assertEqual(expected_data, data, msg=data)


class UserBooksOffersListSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.library_2 = Libraries.objects.create(
            title='Test Library 2',
            location='Test location 2',
            phone='2-111-111-11-11'
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Testdis1')
        self.offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_2,
                                                    quantity=2, books_description='Testdis2')

    def test_ok(self):
        expected_data = [
            {
                'user': 'User1',
                'library': 'Test Library 1',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.offer_1.created_at),
                'url': f'/api/v1/user-offers/{self.offer_1.id}/'
            },
            {
                'user': 'User1',
                'library': 'Test Library 2',
                'is_accepted': False,
                'is_closed': False,
                'created_at': str(self.offer_1.created_at),
                'url': f'/api/v1/user-offers/{self.offer_2.id}/'
            }
        ]
        data = UserBooksOffersListSerializer([self.offer_1, self.offer_2],
                                             many=True, context={'request': None}).data
        for session in data:
            session['created_at'] = str(self.offer_1.created_at)
        self.assertEqual(expected_data, data, msg=data)


class UserBooksOfferEditSerializerTestCase(TestCase):

    def setUp(self):
        self.library_1 = Libraries.objects.create(
            title='Test Library 1',
            location='Test location 1',
            phone='1-111-111-11-11'
        )
        self.user_1 = User.objects.create_user(username='User1', password='testpass')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Testdis1')

    def test_ok(self):
        expected_data = {
            'user': 'User1',
            'library': self.library_1.id,
            'quantity': 1,
            'books_description': 'Testdis1',
            'is_accepted': False,
            'is_closed': False,
            'message': '-',
            'created_at': str(self.offer_1.created_at)
        }
        data = UserBooksOfferEditSerializer(self.offer_1).data
        data['created_at'] = str(self.offer_1.created_at)
        self.assertEqual(expected_data, data, msg=data)

    def test_validate_valid_data(self):
        offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                               quantity=2, books_description='Testdis2')
        valid_data = {
            'is_accepted': True,
            'message': 'Test message',
        }
        data = UserBooksOfferEditSerializer.validate(self=UserBooksOfferEditSerializer(instance=offer_2),
                                                     data=valid_data)
        self.assertEqual(valid_data, data)

    def test_validate_cancel_accept(self):
        offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                               quantity=2, books_description='Testdis2', is_accepted=True)
        not_valid_data = {
            'is_accepted': False
        }
        with self.assertRaises(ValidationError):
            UserBooksOfferEditSerializer.validate(self=UserBooksOfferEditSerializer(instance=offer_2),
                                                  data=not_valid_data)

    def test_validate_change_closed(self):
        offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                               quantity=2, books_description='Testdis2', is_closed=True)
        not_valid_data = {
            'is_closed': False
        }
        with self.assertRaises(ValidationError):
            UserBooksOfferEditSerializer.validate(self=UserBooksOfferEditSerializer(instance=offer_2),
                                                  data=not_valid_data)
