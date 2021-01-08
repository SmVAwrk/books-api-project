from django.test import TestCase

from books.models import Books, Authors, Categories, User
from books.serializers import BooksListSerializer


class BooksListSerializerTestCase(TestCase):

    def setUp(self):
        pass

    def test_ok(self):
        user_1 = User.objects.create(
            username='testuser1',
            password='testpass'
        )
        user_2 = User.objects.create(
            username='testuser2',
            password='testpass'
        )
        author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        author_2 = Authors.objects.create(
            first_name='Test',
            last_name='Author 2'
        )
        category_1 = Categories.objects.create(title='Test category 1')
        category_2 = Categories.objects.create(title='Test category 2')
        book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=author_1,
            owner=user_1
        )
        book_1.categories.add(category_1)

        book_2 = Books.objects.create(
            title='Test book 2',
            description='Test description 2',
            author=author_2,
            owner=user_2
        )
        book_2.categories.add(category_2)

        data = BooksListSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'Test book 1',
                'author': 'Author 1',
            },
            {
                'id': book_2.id,
                'title': 'Test book 2',
                'author': 'Author 2',
            },
        ]
        self.assertEqual(expected_data, data)