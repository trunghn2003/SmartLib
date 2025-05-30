import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Book, Category, User, Reader
from .serializers import BookSerializer

class BookInfoListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_book_info')

        # Tạo category, user và reader
        self.category = Category.objects.create(category_name='TestCategory')
        self.user = User.objects.create(
            user_name='testuser', email='test@example.com', user_password='pass', is_active=True
        )
        self.reader = Reader.objects.create(user=self.user, reader_point=0, reader_rank='Bronze')

        # Tạo một sách mẫu để test thành công
        self.book = Book.objects.create(
            book_name='Sample Book',
            book_author='Author',
            book_type='Fiction',
            book_barcode='BARCODE123',
            book_description='Description',
            category=self.category,
            status=Book.Status.ACCEPTED
        )

    def test_get_book_info_success(self):
        """
        Test lấy thông tin sách thành công
        Mã Test: UT-BILV-01
        Input:
        - book_id hợp lệ qua query params
        Expected Output:
        - Status code 200
        - Response JSON khớp serializer data
        """
        response = self.client.get(self.url, {'book_id': self.book.book_id})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        expected = BookSerializer(self.book).data
        self.assertEqual(result, expected)

    def test_get_book_info_not_found(self):
        """
        Test lấy thông tin sách không tồn tại
        Mã Test: UT-BILV-02
        Input:
        - book_id không tồn tại
        Expected Output:
        - Book.DoesNotExist exception được ném lên
        """
        from .models import Book
        # Expect Book.DoesNotExist since view does not catch it
        with self.assertRaises(Book.DoesNotExist):
            self.client.get(self.url, {'book_id': 99999})

    def test_reader_does_not_exist_branch(self):
        """
        Test xử lý khi Book.objects.get ném Reader.DoesNotExist
        Mã Test: UT-BILV-03
        Kỹ thuật: patch Book.objects.get để ném Reader.DoesNotExist
        Expected Output:
        - Status code 400
        - Response JSON {'error': 'Book not found'}
        """
        from unittest.mock import patch
        import smartlib_api.views as views_module
        # Patch get() to raise Reader.DoesNotExist
        with patch.object(views_module.Book.objects, 'get', side_effect=views_module.Reader.DoesNotExist):
            response = self.client.get(self.url, {'book_id': self.book.book_id})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'error': 'Book not found'})