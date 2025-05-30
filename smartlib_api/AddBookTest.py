from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import (
    User, Reader, Book, Category, UploadedBook,
    Gamification_Record, Notification
)
import logging

# Tắt log mặc định của Django test client (POST/FILES debug)
logging.getLogger('django.request').setLevel(logging.CRITICAL)

class AddBookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('add_book')

        self.book_file = SimpleUploadedFile("book.pdf", b"file_content", content_type="application/pdf")
        self.book_image = SimpleUploadedFile("image.jpg", b"image_content", content_type="image/jpeg")

        self.category = Category.objects.create(category_name="Tech")
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password="hashed_pw",
            is_active=True
        )
        self.reader = Reader.objects.create(user=self.user, reader_point=0, reader_rank="Bronze")

        self.base_data = {
            'title': 'My Book',
            'author': 'John Doe',
            'barcode': '987654321',
            'description': 'A sample book',
            'category': self.category.category_id,
            'bookfile': self.book_file,
            'bookImage': self.book_image,
            'reader_id': self.reader.reader_id
        }

    def test_add_book_success(self):
        """
        Test thêm sách thành công
        Mã Test: UT-AB-01
        Input:
        - Đầy đủ dữ liệu hợp lệ
        Expected Output:
        - Status code 200
        - JSON chứa 'book_id' và status 'success'
        """
        response = self.client.post(self.url, self.base_data, format='multipart')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('book_id', data)

        book = Book.objects.get(book_id=data['book_id'])
        self.assertEqual(book.book_name, 'My Book')
        self.assertEqual(book.book_author, 'John Doe')
        self.assertTrue(book.book_file)
        self.assertTrue(book.book_image)

    def test_missing_category(self):
        """
        Test category không hợp lệ
        Mã Test: UT-AB-02
        Input:
        - Category ID không tồn tại
        Expected Output:
        - Status code 400
        - Message: 'Invalid category.'
        """
        data = self.base_data.copy()
        data['category'] = 9999
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid category.')

    def test_missing_required_field(self):
        """
        Test thiếu các trường bắt buộc
        Mã Test: UT-AB-03
        Input:
        - Thiếu lần lượt từng trường: title, author, barcode, description, category, bookfile
        Expected Output:
        - Status code 500
        - Thông báo lỗi
        """
        for field in ['title', 'author', 'barcode', 'description', 'category', 'bookfile']:
            data = self.base_data.copy()
            if field in data:
                data.pop(field)
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, 500)
            self.assertIn('message', response.json())

    def test_no_image_uploaded(self):
        """
        Test không gửi ảnh bìa sách
        Mã Test: UT-AB-04
        Input:
        - Thiếu trường bookImage
        Expected Output:
        - Status code 200
        - Tạo sách thành công, image = None
        """
        data = self.base_data.copy()
        data.pop('bookImage')
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        book = Book.objects.latest('book_id')
        self.assertTrue(book.book_file)
        self.assertIsNone(book.book_image)

    def test_invalid_method(self):
        """
        Test sử dụng method không hợp lệ
        Mã Test: UT-AB-05
        Input:
        - Gửi request bằng GET
        Expected Output:
        - Status code 405
        - Message: 'Invalid request method.'
        """
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['message'], 'Invalid request method.')

    def test_reader_point_and_rank_update(self):
        """
        Test cập nhật điểm và hạng cho reader
        Mã Test: UT-AB-06
        Input:
        - Reader có điểm 0, 1450, 2950
        Expected Output:
        - Điểm tăng thêm 50
        - Rank cập nhật tương ứng (Bronze → Silver → Gold)
        """
        test_cases = [
            (0, 50, 'Bronze'),
            (1450, 1500, 'Silver'),
            (2950, 3000, 'Gold'),
        ]
        for initial_point, expected_point, expected_rank in test_cases:
            self.reader.reader_point = initial_point
            self.reader.reader_rank = "Bronze"
            self.reader.save()

            data = self.base_data.copy()
            data['barcode'] = str(initial_point)
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, 200)

            self.reader.refresh_from_db()
            self.assertEqual(self.reader.reader_point, expected_point)
            self.assertEqual(self.reader.reader_rank, expected_rank)

    def test_uploadedbook_and_notification_created(self):
        """
        Test tạo bản ghi UploadedBook, Gamification_Record, Notification
        Mã Test: UT-AB-07
        Input:
        - Đầy đủ dữ liệu sách hợp lệ
        Expected Output:
        - 1 bản ghi UploadedBook
        - 1 bản ghi Gamification_Record với +50 điểm
        - 1 bản ghi Notification tương ứng
        """
        data = self.base_data.copy()
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        book_id = response.json()['book_id']

        uploaded = UploadedBook.objects.filter(book_id=book_id, reader_id=self.reader.reader_id).first()
        self.assertIsNotNone(uploaded)

        gamification = Gamification_Record.objects.filter(reader_id=self.reader.reader_id).first()
        self.assertIsNotNone(gamification)
        self.assertEqual(gamification.achieved_point, 50)

        notification = Notification.objects.filter(reader_id=self.reader.reader_id).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_title, 'New Point Achievement')

    def tearDown(self):
        for book in Book.objects.all():
            if book.book_file:
                book.book_file.delete(save=False)
            if book.book_image:
                book.book_image.delete(save=False)
