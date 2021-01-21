from django.test import TestCase

from books.models import Authors, Books, UserBookRelation, User
from books.serializers import UserBookRelationSerializer
from books.services import set_rating, set_likes, set_bookmarks, set_book_values


class SetRatingTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_2 = User.objects.create_user(username='User2', password='password')
        self.user_3 = User.objects.create_user(username='User3', password='password')
        self.user_4 = User.objects.create_user(username='User4', password='password')
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_relation_1 = UserBookRelation.objects.create(user=self.user_1, book=self.book_1, rate=5)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, rate=3)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1, rate=4)
        UserBookRelation.objects.create(user=self.user_4, book=self.book_1)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.00', str(self.book_1.rating))

    def test_change_rate(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.book_relation_1.rate = 4
        self.book_relation_1.save()
        self.book_relation_1.refresh_from_db()
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('3.67', str(self.book_1.rating))


class SetLikesTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_2 = User.objects.create_user(username='User2', password='password')
        self.user_3 = User.objects.create_user(username='User3', password='password')
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.book_relation_1 = UserBookRelation.objects.create(user=self.user_1, book=self.book_1, like=True)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, like=True)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1, rate=4)

    def test_ok(self):
        set_likes(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(2, self.book_1.likes)

    def test_change_like(self):
        set_likes(self.book_1)
        self.book_1.refresh_from_db()
        self.book_relation_1.like = False
        self.book_relation_1.save()
        self.book_relation_1.refresh_from_db()
        set_likes(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(1, self.book_1.likes)


class SetBookmarksTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.user_2 = User.objects.create_user(username='User2', password='password')
        self.user_3 = User.objects.create_user(username='User3', password='password')
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, in_bookmarks=True)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, like=True, in_bookmarks=True)
        self.book_relation_3 = UserBookRelation.objects.create(user=self.user_3, book=self.book_1, rate=4)

    def test_ok(self):
        set_bookmarks(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(2, self.book_1.bookmarks)

    def test_change_bookmarks(self):
        set_bookmarks(self.book_1)
        self.book_1.refresh_from_db()
        self.book_relation_3.in_bookmarks = True
        self.book_relation_3.save()
        self.book_relation_3.refresh_from_db()
        set_bookmarks(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(3, self.book_1.bookmarks)


class SetBookValuesTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='User1', password='password')
        self.author_1 = Authors.objects.create(
            first_name='Test',
            last_name='Author 1'
        )
        self.book_1 = Books.objects.create(
            title='Test book 1',
            description='Test description 1',
            author=self.author_1,
        )
        self.relation_1, self.created = UserBookRelation.objects.get_or_create(user=self.user_1, book=self.book_1,
                                                                               in_bookmarks=True)

    def test_ok_create(self):
        serializer = UserBookRelationSerializer(self.relation_1)
        set_book_values(serializer, self.created)
        self.book_1.refresh_from_db()
        self.assertEqual(None, self.book_1.rating)
        self.assertEqual(0, self.book_1.likes)
        self.assertEqual(1, self.book_1.bookmarks)

    def test_ok_update(self):
        data = {
            'like': True,
            'in_bookmarks': False,
            'rate': 5
        }
        serializer = UserBookRelationSerializer(instance=self.relation_1, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
        set_book_values(serializer, False)
        self.book_1.refresh_from_db()
        self.assertEqual('5.00', str(self.book_1.rating))
        self.assertEqual(1, self.book_1.likes)
        self.assertEqual(0, self.book_1.bookmarks)
