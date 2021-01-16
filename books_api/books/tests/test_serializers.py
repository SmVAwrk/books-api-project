from django.test import TestCase
from rest_framework.reverse import reverse

from books.models import Books, Authors, Categories, User
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
            last_name='Author 2'
        )

    def test_ok(self):
        expected_data = [
            {
                'full_name': 'Test Author 1',
                'url': f'/api/v1/authors/{self.author_1.id}/books/'
            },
            {
                'full_name': 'Test Author 2',
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