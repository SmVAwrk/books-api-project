import datetime
import json

from django.db.models import Count, Case, When
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import (
    Authors, User, Categories,
    Books, Libraries, BookLibraryAvailable,
    UserBookRelation, UserBookSession, UserBookOffer
)
from books.serializers import (
    BooksListSerializer, BooksDetailSerializer, BookCreateSerializer, AuthorsListSerializer,
    AuthorDetailSerializer, CategoriesListSerializer, CategoryDetailSerializer, LibrariesListSerializer,
    LibraryDetailSerializer, MyBooksSessionsListSerializer, MyBooksSessionDetailSerializer,
    UserBooksSessionsListSerializer, UserBooksSessionsEditSerializer, LibraryCreateSerializer, AuthorCreateSerializer,
    CategoryCreateSerializer, BooksSessionCreateSerializer, BooksLibrariesAvailableListSerializer,
    BooksLibrariesAvailableDetailSerializer, BooksLibrariesAvailableEditSerializer, UserBookRelationSerializer,
    MyBooksOffersListSerializer, MyBooksOfferDetailSerializer, MyBooksOfferCreateSerializer,
    UserBooksOffersListSerializer, UserBooksOfferEditSerializer
)


class BooksViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)
        self.library_1 = Libraries.objects.create(title='Lib 1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib 2', location='Loc 2', phone='Phone 2')
        self.book_available_1 = BookLibraryAvailable.objects.create(book=self.book_1, library=self.library_1,
                                                                    available=True)
        self.book_available_2 = BookLibraryAvailable.objects.create(book=self.book_1, library=self.library_2,
                                                                    available=False)
        self.book_available_3 = BookLibraryAvailable.objects.create(book=self.book_2, library=self.library_2,
                                                                    available=True)

    def test_list(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Books.objects.filter(lib_available__available=True).select_related('author').prefetch_related(
            'categories').distinct()
        serializer_data = BooksListSerializer(books, many=True, context={'request': response.wsgi_request}).data
        # response.wsgi_request - под вопросом
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Book 1'})
        books = Books.objects.filter(title__contains='Book 1',
                                     lib_available__available=True).select_related('author').prefetch_related(
            'categories').distinct()
        serializer_data = BooksListSerializer(books, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'categories': self.category_1.id})
        books = Books.objects.filter(categories__in=[self.category_1.id],
                                     lib_available__available=True).select_related('author').prefetch_related(
            'categories').distinct()
        serializer_data = BooksListSerializer(books, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_ordering(self):
        UserBookRelation.objects.create(book=self.book_1, user=self.user_1, rate=5)
        UserBookRelation.objects.create(book=self.book_2, user=self.user_1, rate=3)
        UserBookRelation.objects.create(book=self.book_3, user=self.user_1, rate=4)
        BookLibraryAvailable.objects.create(book=self.book_3, library=self.library_2, available=True)
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-rating'})
        books = Books.objects.filter(lib_available__available=True).select_related('author').prefetch_related(
            'categories').distinct().order_by('-rating')
        serializer_data = BooksListSerializer(books, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('book-detail', kwargs={'pk': self.book_1.id})
        response = self.client.get(path=url)
        books = Books.objects.filter(pk=self.book_1.id).annotate(
            reading_now=Count(Case(When(session_books__is_accepted=True,
                                        session_books__is_closed=False,
                                        then=1))),
        ).select_related('author').prefetch_related('categories', 'lib_available__library')
        serializer_data = BooksDetailSerializer(books[0], context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_not_admin(self):
        url = reverse('book-list')
        self.client.force_login(self.user_1)
        created_data = {
            'title': 'Book 4',
            'description': 'Desc 4',
            'author': self.author_1.id,
            'category': [
                self.category_1.id
            ]
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_admin(self):
        url = reverse('book-list')
        self.client.force_login(self.user_staff)
        created_data = {
            'title': 'Book 4',
            'description': 'Desc 4',
            'author': self.author_1.id,
            'category': [
                self.category_1.id
            ]
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        book = Books.objects.order_by('-id').first()
        serializer_data = BookCreateSerializer(book, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)

    def test_update_not_admin(self):
        url = reverse('book-detail', kwargs={'pk': self.book_1.id})
        self.client.force_login(self.user_1)
        created_data = {
            'title': 'Test Book 1',
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_admin(self):
        url = reverse('book-detail', kwargs={'pk': self.book_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'title': 'Test Book 1',
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        book = Books.objects.get(pk=self.book_1.id)
        serializer_data = BookCreateSerializer(book, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual('Test Book 1', Books.objects.get(pk=self.book_1.id).title)

    def test_destroy_not_admin(self):
        url = reverse('book-detail', kwargs={'pk': self.book_1.id})
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_destroy_admin(self):
        url = reverse('book-detail', kwargs={'pk': self.book_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class AuthorsViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)

    def test_list(self):
        url = reverse('author-list')
        response = self.client.get(url)
        authors = Authors.objects.all()
        serializer_data = AuthorsListSerializer(authors, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('author-list')
        response = self.client.get(url, data={'search': 'Author 2'})
        authors = Authors.objects.filter(last_name__contains='Author 2')
        serializer_data = AuthorsListSerializer(authors, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('author-detail', kwargs={'pk': self.author_1.id})
        response = self.client.get(path=url)
        author = Authors.objects.get(pk=self.author_1.id)
        serializer_data = AuthorDetailSerializer(author, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_books(self):
        url = reverse('author-books', kwargs={'pk': self.author_1.id})
        response = self.client.get(path=url)
        books_by_author = Books.objects.filter(author=self.author_1.id).select_related('author').prefetch_related(
            'categories')
        serializer_data = BooksListSerializer(books_by_author, many=True,
                                              context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_create_not_admin(self):
        url = reverse('author-list')
        self.client.force_login(self.user_1)
        created_data = {
            'first_name': 'Test',
            'last_name': 'Author 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_admin(self):
        url = reverse('author-list')
        self.client.force_login(self.user_staff)
        created_data = {
            'first_name': 'Test',
            'last_name': 'Author 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        author = Authors.objects.order_by('-id').first()
        serializer_data = AuthorCreateSerializer(author, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)

    def test_update_not_admin(self):
        url = reverse('author-detail', kwargs={'pk': self.author_1.id})
        self.client.force_login(self.user_1)
        created_data = {
            'last_name': 'Test Author 3',
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_admin(self):
        url = reverse('author-detail', kwargs={'pk': self.author_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'last_name': 'Test Author 3',
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        author = Authors.objects.get(pk=self.author_1.id)
        serializer_data = AuthorCreateSerializer(author, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual('Test Author 3', author.last_name)

    def test_destroy_not_admin(self):
        url = reverse('author-detail', kwargs={'pk': self.author_1.id})
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_destroy_admin(self):
        url = reverse('author-detail', kwargs={'pk': self.author_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class CategoriesViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)

    def test_list(self):
        url = reverse('category-list')
        response = self.client.get(url)
        categories = Categories.objects.all()
        serializer_data = CategoriesListSerializer(categories, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('category-list')
        response = self.client.get(url, data={'search': 'Category 1'})
        categories = Categories.objects.filter(title__contains='Category 1')
        serializer_data = CategoriesListSerializer(categories, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('category-detail', kwargs={'pk': self.category_1.id})
        response = self.client.get(url)
        category = Categories.objects.get(pk=self.category_1.id)
        serializer_data = CategoryDetailSerializer(category, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_books(self):
        url = reverse('category-books', kwargs={'pk': self.category_1.id})
        response = self.client.get(path=url)
        books_by_category = Books.objects.filter(categories=self.category_1.id).select_related('author').prefetch_related(
            'categories')
        serializer_data = BooksListSerializer(books_by_category, many=True,
                                              context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_create_not_admin(self):
        url = reverse('category-list')
        self.client.force_login(self.user_1)
        created_data = {
            'title': 'Category 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_admin(self):
        url = reverse('category-list')
        self.client.force_login(self.user_staff)
        created_data = {
            'title': 'Category 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        category = Categories.objects.order_by('-id').first()
        serializer_data = CategoryCreateSerializer(category, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)

    def test_update_not_admin(self):
        url = reverse('category-detail', kwargs={'pk': self.category_1.id})
        self.client.force_login(self.user_1)
        created_data = {
            'title': 'Test Category 1'
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_admin(self):
        url = reverse('category-detail', kwargs={'pk': self.category_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'title': 'Test Category 1'
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        category = Categories.objects.get(pk=self.category_1.id)
        serializer_data = CategoryCreateSerializer(category, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual('Test Category 1', category.title)

    def test_destroy_not_admin(self):
        url = reverse('category-detail', kwargs={'pk': self.category_1.id})
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_destroy_admin(self):
        url = reverse('category-detail', kwargs={'pk': self.category_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class LibrariesViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)
        self.library_1 = Libraries.objects.create(title='Lib 1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib 2', location='Loc 2', phone='Phone 2')

    def test_list(self):
        url = reverse('library-list')
        response = self.client.get(url)
        libraries = Libraries.objects.all()
        serializer_data = LibrariesListSerializer(libraries, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('library-list')
        response = self.client.get(url, data={'search': 'Lib 1'})
        libraries = Libraries.objects.filter(title__contains='Lib 1')
        serializer_data = LibrariesListSerializer(libraries, many=True,
                                                  context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('library-detail', kwargs={'pk': self.library_1.id})
        response = self.client.get(url)
        library = Libraries.objects.get(pk=self.library_1.id)
        serializer_data = LibraryDetailSerializer(library, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_books(self):
        url = reverse('library-books', kwargs={'pk': self.library_1.id})
        response = self.client.get(url)
        books_by_library = Books.objects.filter(lib_available__library=self.library_1.id).select_related(
            'author').prefetch_related('categories')
        serializer_data = BooksListSerializer(books_by_library, many=True,
                                              context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_create_not_admin(self):
        url = reverse('library-list')
        self.client.force_login(self.user_1)
        created_data = {
            'title': 'Lib 3',
            'location': 'Loc 3',
            'phone': 'Phone 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_create_admin(self):
        url = reverse('library-list')
        self.client.force_login(self.user_staff)
        created_data = {
            'title': 'Lib 3',
            'location': 'Loc 3',
            'phone': 'Phone 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        library = Libraries.objects.order_by('-id').first()
        serializer_data = LibraryCreateSerializer(library, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)

    def test_update_not_admin(self):
        url = reverse('library-detail', kwargs={'pk': self.library_1.id})
        self.client.force_login(self.user_1)
        created_data = {
            'location': 'Test Loc 1'
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_admin(self):
        url = reverse('library-detail', kwargs={'pk': self.library_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'location': 'Test Loc 1'
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        library = Libraries.objects.get(pk=self.library_1.id)
        serializer_data = LibraryCreateSerializer(library, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual('Test Loc 1', library.location)

    def test_destroy_not_admin(self):
        url = reverse('library-detail', kwargs={'pk': self.library_1.id})
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_destroy_admin(self):
        url = reverse('library-detail', kwargs={'pk': self.library_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class MySessionsViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)
        self.library_1 = Libraries.objects.create(title='Lib 1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib 2', location='Loc 2', phone='Phone 2')
        BookLibraryAvailable.objects.create(book=self.book_1, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_2, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_3, library=self.library_2, available=True)
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)
        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_2,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end, is_accepted=True)
        self.session_1.books.add(self.book_1, self.book_2)
        self.session_2.books.add(self.book_3)

    def test_list_not_auth(self):
        url = reverse('my-session-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_auth(self):
        url = reverse('my-session-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        sessions = UserBookSession.objects.filter(user=self.user_1).select_related('user', 'library')
        serializer_data = MyBooksSessionsListSerializer(sessions, many=True,
                                                        context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_filter(self):
        url = reverse('my-session-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url, data={'is_accepted': True})
        sessions = UserBookSession.objects.filter(user=self.user_1, is_accepted=True).select_related('user', 'library')
        serializer_data = MyBooksSessionsListSerializer(sessions, many=True,
                                                        context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('my-session-detail', kwargs={'pk': self.session_1.id})
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        session = UserBookSession.objects.get(pk=self.session_1.id)
        serializer_data = MyBooksSessionDetailSerializer(session, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('my-session-list')
        self.client.force_login(self.user_1)
        created_data = {
            'books': [
                self.book_3.id
            ],
            'library': self.library_2.id,
            'start_date': str(self.test_start),
            'end_date': str(self.test_end)
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        session = UserBookSession.objects.order_by('-id').first()
        serializer_data = BooksSessionCreateSerializer(session, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)


class UserSessionsViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)
        self.library_1 = Libraries.objects.create(title='Lib1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib2', location='Loc 2', phone='Phone 2')
        BookLibraryAvailable.objects.create(book=self.book_1, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_2, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_3, library=self.library_2, available=True)
        self.test_start = datetime.datetime.now().date()
        self.test_end = self.test_start + datetime.timedelta(days=7)
        self.session_1 = UserBookSession.objects.create(user=self.user_1, library=self.library_1,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end)
        self.session_2 = UserBookSession.objects.create(user=self.user_1, library=self.library_2,
                                                        start_date=self.test_start,
                                                        end_date=self.test_end, is_accepted=True)
        self.session_1.books.add(self.book_1, self.book_2)
        self.session_2.books.add(self.book_3)

    def test_list_not_admin(self):
        url = reverse('user-session-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_admin(self):
        url = reverse('user-session-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        sessions = UserBookSession.objects.all().select_related('user', 'library')
        serializer_data = UserBooksSessionsListSerializer(sessions, many=True,
                                                          context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('user-session-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url, data={'search': 'Lib1'})
        sessions = UserBookSession.objects.filter(library__title__contains='Lib1').select_related('user', 'library')
        serializer_data = UserBooksSessionsListSerializer(sessions, many=True,
                                                          context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'], f'\n{serializer_data}\n{response.data["results"]}')

    def test_list_filter(self):
        url = reverse('user-session-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url, data={'is_accepted': False})
        sessions = UserBookSession.objects.filter(is_accepted=False).select_related('user', 'library')
        serializer_data = UserBooksSessionsListSerializer(sessions, many=True,
                                                          context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('user-session-detail', kwargs={'pk': self.session_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        session = UserBookSession.objects.get(pk=self.session_1.id)
        serializer_data = MyBooksSessionDetailSerializer(session, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('user-session-detail', kwargs={'pk': self.session_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'is_accepted': True
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        session = UserBookSession.objects.get(pk=self.session_1.id)
        serializer_data = UserBooksSessionsEditSerializer(session, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertTrue(session.is_accepted)

    def test_destroy(self):
        url = reverse('user-session-detail', kwargs={'pk': self.session_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class BooksLibrariesAvailableViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.author_2 = Authors.objects.create(first_name='Test', last_name='Author 2')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.category_2 = Categories.objects.create(title='Category 2')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_2)
        self.book_2.categories.add(self.category_1, self.category_2)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_2)
        self.book_3.categories.add(self.category_2)
        self.library_1 = Libraries.objects.create(title='Lib1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib2', location='Loc 2', phone='Phone 2')
        self.available_1 = BookLibraryAvailable.objects.create(book=self.book_1, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_2, library=self.library_1, available=True)
        BookLibraryAvailable.objects.create(book=self.book_3, library=self.library_2, available=True)

    def test_list_not_admin(self):
        url = reverse('available-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_admin(self):
        url = reverse('available-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        available_relations = BookLibraryAvailable.objects.all().select_related('book', 'library')
        serializer_data = BooksLibrariesAvailableListSerializer(available_relations, many=True,
                                                                context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_filter(self):
        url = reverse('available-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url, data={'book': self.book_1.id})
        available_relations = BookLibraryAvailable.objects.filter(book=self.book_1).select_related('book', 'library')
        serializer_data = BooksLibrariesAvailableListSerializer(available_relations, many=True,
                                                                context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('available-detail', kwargs={'pk': self.available_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        available_relation = BookLibraryAvailable.objects.get(pk=self.available_1.id)
        serializer_data = BooksLibrariesAvailableDetailSerializer(available_relation, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('available-list')
        self.client.force_login(self.user_staff)
        created_data = {
            'book': self.book_1.id,
            'library': self.library_2.id,
            'available': True
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        available_relation = BookLibraryAvailable.objects.order_by('-id').first()
        serializer_data = BooksLibrariesAvailableEditSerializer(available_relation,
                                                       context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('available-detail', kwargs={'pk': self.available_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'available': False
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        available_relation = BookLibraryAvailable.objects.get(pk=self.available_1.id)
        serializer_data = BooksLibrariesAvailableEditSerializer(available_relation,
                                                                context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertFalse(available_relation.available)

    def test_destroy(self):
        url = reverse('available-detail', kwargs={'pk': self.available_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class UserBookRelationViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)

    def test_update_not_auth(self):
        url = reverse('book-relation-detail', kwargs={'book': self.book_1.id})
        updated_data = {
            'book': self.book_1.id,
            'like': True
        }
        json_data = json.dumps(updated_data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_update(self):
        url = reverse('book-relation-detail', kwargs={'book': self.book_1.id})
        self.client.force_login(self.user_1)
        updated_data = {
            'book': self.book_1.id,
            'like': True
        }
        json_data = json.dumps(updated_data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        book_relation = UserBookRelation.objects.get(user=self.user_1, book=self.book_1)
        serializer_data = UserBookRelationSerializer(book_relation).data
        self.assertEqual(serializer_data, response.data, f'\n{serializer_data}\n{response.data}')
        self.assertTrue(book_relation.like)


class MyOffersViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.library_1 = Libraries.objects.create(title='Lib 1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib 2', location='Loc 2', phone='Phone 2')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Test Desc 1')
        self.offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_2,
                                                    quantity=2, books_description='Test Desc 1', is_accepted=True)

    def test_list_not_auth(self):
        url = reverse('my-offer-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_auth(self):
        url = reverse('my-offer-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        offers = UserBookOffer.objects.filter(user=self.user_1).select_related('user', 'library')
        serializer_data = MyBooksOffersListSerializer(offers, many=True,
                                                      context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_filter(self):
        url = reverse('my-offer-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url, data={'is_accepted': True})
        offers = UserBookOffer.objects.filter(user=self.user_1, is_accepted=True).select_related('user', 'library')
        serializer_data = MyBooksOffersListSerializer(offers, many=True,
                                                      context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('my-offer-detail', kwargs={'pk': self.offer_1.id})
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        offer = UserBookOffer.objects.get(pk=self.offer_1.id)
        serializer_data = MyBooksOfferDetailSerializer(offer, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('my-offer-list')
        self.client.force_login(self.user_1)
        created_data = {
            'library': self.library_1.id,
            'quantity': 3,
            'books_description': 'Test Desc 3'
        }
        json_data = json.dumps(created_data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        offer = UserBookOffer.objects.order_by('-id').first()
        serializer_data = MyBooksOfferCreateSerializer(offer, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)


class UserOffersViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_staff = User.objects.create_user(username='StaffUser', password='password', is_staff=True)
        self.library_1 = Libraries.objects.create(title='Lib1', location='Loc 1', phone='Phone 1')
        self.library_2 = Libraries.objects.create(title='Lib2', location='Loc 2', phone='Phone 2')
        self.offer_1 = UserBookOffer.objects.create(user=self.user_1, library=self.library_1,
                                                    quantity=1, books_description='Test Desc 1')
        self.offer_2 = UserBookOffer.objects.create(user=self.user_1, library=self.library_2,
                                                    quantity=2, books_description='Test Desc 1', is_accepted=True)

    def test_list_not_admin(self):
        url = reverse('user-offer-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_admin(self):
        url = reverse('user-offer-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        offers = UserBookOffer.objects.all().select_related('user', 'library')
        serializer_data = UserBooksOffersListSerializer(offers, many=True,
                                                        context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_search(self):
        url = reverse('user-offer-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url, data={'search': 'Lib1'})
        offers = UserBookOffer.objects.filter(library__title__contains='Lib1').select_related('user', 'library')
        serializer_data = UserBooksOffersListSerializer(offers, many=True,
                                                        context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_list_filter(self):
        url = reverse('user-offer-list')
        self.client.force_login(self.user_staff)
        response = self.client.get(url, data={'is_accepted': False})
        offers = UserBookOffer.objects.filter(is_accepted=False).select_related('user', 'library')
        serializer_data = UserBooksOffersListSerializer(offers, many=True,
                                                        context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('user-offer-detail', kwargs={'pk': self.offer_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.get(url)
        offer = UserBookOffer.objects.get(pk=self.offer_1.id)
        serializer_data = MyBooksOfferDetailSerializer(offer, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('user-offer-detail', kwargs={'pk': self.offer_1.id})
        self.client.force_login(self.user_staff)
        created_data = {
            'is_accepted': True
        }
        json_data = json.dumps(created_data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        offer = UserBookOffer.objects.get(pk=self.offer_1.id)
        serializer_data = UserBooksOfferEditSerializer(offer, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data)
        self.assertTrue(offer.is_accepted)

    def test_destroy(self):
        url = reverse('user-offer-detail', kwargs={'pk': self.offer_1.id})
        self.client.force_login(self.user_staff)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class MyBookmarksViewSetTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.author_1 = Authors.objects.create(first_name='Test', last_name='Author 1')
        self.category_1 = Categories.objects.create(title='Category 1')
        self.book_1 = Books.objects.create(title='Book 1', description='Desc1', author=self.author_1)
        self.book_1.categories.add(self.category_1)
        self.book_2 = Books.objects.create(title='Book 2', description='Desc2', author=self.author_1)
        self.book_2.categories.add(self.category_1)
        self.book_3 = Books.objects.create(title='Book 3', description='Desc3', author=self.author_1)
        self.book_3.categories.add(self.category_1)
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, in_bookmarks=True)
        UserBookRelation.objects.create(user=self.user_1, book=self.book_2, in_bookmarks=True, like=True)
        UserBookRelation.objects.create(user=self.user_1, book=self.book_3, rate=3)

    def test_list_not_auth(self):
        url = reverse('my-bookmark-list')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list(self):
        url = reverse('my-bookmark-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        bookmarks = Books.objects.filter(userbookrelation__user=self.user_1,
                                         userbookrelation__in_bookmarks=True).select_related(
            'author').prefetch_related('categories')
        serializer_data = BooksListSerializer(bookmarks, many=True, context={'request': response.wsgi_request}).data
        self.assertEqual(serializer_data, response.data['results'])

    def test_retrieve(self):
        url = reverse('my-bookmark-detail', kwargs={'pk': self.book_1.id})
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        book = Books.objects.get(pk=self.book_1.id)
        serializer_data = BooksDetailSerializer(book, context={'request': response.wsgi_request}).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


