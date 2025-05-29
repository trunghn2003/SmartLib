from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Category, Reader, Book, Manager, UploadedBook, Gamification_Record, Notification
from django.utils.timezone import now
import json

class AddBookTest(TestCase):    
    def setUp(self):
        """Khởi tạo môi trường test
        Thiết lập các đối tượng và dữ liệu cần thiết cho việc test:
        - Tạo category test
        - Tạo reader test
        - Tạo manager test
        - Tạo file và ảnh test
        - Chuẩn bị dữ liệu hợp lệ mẫu"""
        self.client = APIClient()
        self.url = '/add-book/'
        
        # Create test category
        self.category = Category.objects.create(
            category_name="Test Category"
        )
        
        # Create test reader
        self.reader = Reader.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password="hashedpassword",
            reader_rank="Bronze",
            reader_point=0
        )

        # Create test manager for notifications
        Manager.objects.create(
            manager_id=2, 
            user_name="testmanager",
            email="manager@example.com",
            user_password="hashedpassword"
        )

        # Create test files
        self.book_file = SimpleUploadedFile(
            "test_book.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.book_image = SimpleUploadedFile(
            "test_image.jpg",
            b"image_content",
            content_type="image/jpeg"
        )

        # Valid data for reuse
        self.valid_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'barcode': '123456789',
            'description': 'Test Description',
            'category': self.category.category_id,
            'bookfile': self.book_file,
            'bookImage': self.book_image,
            'reader_id': self.reader.reader_id
        }    

    def test_add_book_success(self):
        """Test thêm sách thành công
        Mã Test: UT-AB-01
        Test case này kiểm tra việc thêm sách với đầy đủ thông tin hợp lệ
        Input:
        - Tất cả các trường bắt buộc và tùy chọn đều hợp lệ
        Expected Output:
        - Status code: 200
        - Response thành công với book_id
        - Sách được tạo với đúng thông tin
        - File và ảnh được lưu đúng định dạng"""
        response = self.client.post(self.url, self.valid_data, format='multipart')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Book added successfully!')
        self.assertIn('book_id', data)

        # Verify book creation
        book = Book.objects.get(book_id=data['book_id'])
        self.assertEqual(book.book_name, self.valid_data['title'])
        self.assertEqual(book.book_author, self.valid_data['author'])
        self.assertEqual(book.book_barcode, self.valid_data['barcode'])
        self.assertEqual(book.book_type, self.category.category_name)
        self.assertEqual(book.category_id, self.category.category_id)
        self.assertEqual(book.status, Book.Status.PENDING)

        # Verify initial counters
        self.assertEqual(book.book_reading_counter, 0)
        self.assertEqual(book.book_rating_avg, 0)
        self.assertEqual(book.book_favourite_counter, 0)

        # Verify files
        self.assertTrue(book.book_file)
        self.assertTrue(book.book_image)
        self.assertRegex(book.book_file.name, rf"{book.book_id}_file\.pdf$")
        self.assertRegex(book.book_image.name, rf"{book.book_id}_image\.jpg$")   
    
    def test_add_book_without_image(self):
        """Test thêm sách không có ảnh
        Mã Test: UT-AB-02
        Test case này kiểm tra việc thêm sách không có ảnh bìa (trường tùy chọn)
        Input:
        - Đầy đủ các trường bắt buộc
        - Không có trường bookImage
        Expected Output:
        - Status code: 200
        - Sách được tạo thành công
        - book_image là null"""
        data = self.valid_data.copy()
        data.pop('bookImage')
        
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        
        book = Book.objects.get(book_id=response.json()['book_id'])
        self.assertTrue(book.book_file)
        self.assertFalse(bool(book.book_image))    
        
    def test_invalid_request_method(self):
        """Test phương thức request không hợp lệ
        Mã Test: UT-AB-03
        Test case này kiểm tra việc gọi API với các phương thức không được phép
        Input:
        - Gọi API với phương thức GET
        - Gọi API với phương thức PUT
        Expected Output:
        - Status code: 405
        - Message: Invalid request method"""
        # Test GET method
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['message'], 'Invalid request method.')

        # Test PUT method
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['message'], 'Invalid request method.')    
    
    def test_missing_required_fields(self):
        """Test thiếu trường bắt buộc
        Mã Test: UT-AB-04
        Test case này kiểm tra việc gửi request thiếu các trường bắt buộc
        Input:
        - Lần lượt bỏ đi từng trường bắt buộc
        Expected Output:
        - Status code: 500
        - Response báo lỗi"""
        required_fields = ['title', 'author', 'barcode', 'description', 'category', 'bookfile', 'reader_id']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data.pop(field)
            
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()['status'], 'error')    
            
    def test_invalid_category(self):
        """Test category không hợp lệ
        Mã Test: UT-AB-05
        Test case này kiểm tra việc thêm sách với category không tồn tại
        Input:
        - Category ID không tồn tại
        Expected Output:
        - Status code: 400
        - Message: Invalid category"""
        # Test with non-existent category ID
        data = self.valid_data.copy()
        data['category'] = 99999
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid category.')    
    
    def test_reader_points_update(self):
        """Test cập nhật điểm và rank của reader
        Mã Test: UT-AB-06
        Test case này kiểm tra việc cập nhật điểm và rank của reader sau khi upload sách
        Input:
        - Các mức điểm khác nhau để test các ngưỡng rank
        Expected Output:
        - Điểm tăng 50 cho mỗi lần upload
        - Rank được cập nhật đúng theo ngưỡng điểm"""
        test_cases = [
            (0, 50, "Bronze"),      # Initial
            (480, 530, "Bronze"),   # Still Bronze
            (1480, 1530, "Silver"), # Enter Silver
            (2980, 3030, "Gold"),   # Enter Gold
        ]

        for initial_points, expected_points, expected_rank in test_cases:
            # Reset reader points
            self.reader.reader_point = initial_points
            self.reader.save()

            # Add new book
            data = self.valid_data.copy()
            data['barcode'] = f"TEST{initial_points}"  # Unique barcode
            response = self.client.post(self.url, data, format='multipart')
            
            # Verify points and rank
            self.reader.refresh_from_db()
            self.assertEqual(self.reader.reader_point, expected_points)
            self.assertEqual(self.reader.reader_rank, expected_rank)    
            
    def test_associated_records(self):
        """Test tạo các bản ghi liên quan
        Mã Test: UT-AB-07
        Test case này kiểm tra việc tạo các bản ghi liên quan khi thêm sách thành công
        Input:
        - Request thêm sách hợp lệ
        Expected Output:
        - Bản ghi UploadedBook được tạo với đúng book_id và reader_id
        - Bản ghi Gamification được tạo với 50 điểm
        - Bản ghi Notification được tạo với thông tin chính xác"""
        response = self.client.post(self.url, self.valid_data, format='multipart')
        self.assertEqual(response.status_code, 200)
        book_id = response.json()['book_id']

        # Check UploadedBook record
        uploaded_book = UploadedBook.objects.get(book_id=book_id)
        self.assertEqual(uploaded_book.reader_id, self.reader.reader_id)

        # Check Gamification record
        gamification = Gamification_Record.objects.get(
            reader_id=self.reader.reader_id,
            gamification_description="Upload Books Achievement"
        )
        self.assertEqual(gamification.achieved_point, 50)

        # Check Notification record
        notification = Notification.objects.get(
            reader_id=self.reader.reader_id,
            manager_id=2
        )
        self.assertEqual(notification.notification_title, "New Point Achievement")
        self.assertEqual(notification.notification_record, "+50 Point for Uploaded Books Achievement")    
    
    def test_invalid_reader(self):
        """Test reader không hợp lệ
        Mã Test: UT-AB-08
        Test case này kiểm tra việc thêm sách với reader không tồn tại
        Input:
        - Reader ID không tồn tại trong hệ thống
        Expected Output:
        - Status code: 500
        - Response báo lỗi"""
        data = self.valid_data.copy()
        data['reader_id'] = 99999  # Non-existent reader
        
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['status'], 'error')    
        
    def tearDown(self):
        """Dọn dẹp sau khi test
        - Xóa các file đã tạo trong quá trình test
        - Đảm bảo không có dữ liệu thừa sau khi test"""
        # Clean up files
        for book in Book.objects.all():
            if book.book_file:
                if hasattr(book.book_file.storage, 'delete'):
                    book.book_file.storage.delete(book.book_file.name)
            if book.book_image:
                if hasattr(book.book_image.storage, 'delete'):
                    book.book_image.storage.delete(book.book_image.name)