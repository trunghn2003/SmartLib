from unittest import mock
import json
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
from django.utils import timezone
import datetime
import bcrypt
import jwt
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from .models import User, Reader, Gamification_Record, Notification, Book, Rating_And_Review, Category, Manager, UploadedBook
from .views import AddRatingAndReviewView, UserLoginView, send_another_email, send_verification_email_register, token_generator_register
from unittest.mock import MagicMock, patch, PropertyMock, ANY
from django.core.files.uploadedfile import SimpleUploadedFile
from .pagination import BookPagination, BookSearchPagination

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from django.utils.timezone import now
import bcrypt
from .models import User, Reader, Gamification_Record, Notification, Book, Rating_And_Review, Category, Manager
from .views import AddRatingAndReviewView
from unittest.mock import patch, PropertyMock
# Run test command: python manage.py test smartlib_api.tests.AddRatingAndReviewViewTests -v 2
# Run coverage command: coverage run manage.py test smartlib_api.tests.AddRatingAndReviewViewTests -v 2
# Run coverage report: coverage report -m
# Run .venv command: .venv/Scripts/activate


class BookSearchViewTest(APITestCase):
    """Test cases for BookSearchView"""

    def setUp(self):
        """Set up test data"""
        # Create test categories
        self.category1 = Category.objects.create(category_name="History")
        self.category2 = Category.objects.create(category_name="Sport")
        
        # Create test books
        self.book1 = Book.objects.create(
            book_name="Test History Book",
            book_author="Author 1",
            book_barcode="123456789",
            book_type="History",
            category=self.category1,
            book_rating_avg=4.5,
            book_reading_counter=100,
            book_favourite_counter=50,
            status=Book.Status.ACCEPTED,
            book_uploaded_date="2025-04-17"
        )
        
        self.book2 = Book.objects.create(
            book_name="Test Sport Book",
            book_author="Author 2",
            book_barcode="123456788",
            book_type="Sport",
            category=self.category2,
            book_rating_avg=3.5,
            book_reading_counter=80,
            book_favourite_counter=30,
            status=Book.Status.ACCEPTED,
            book_uploaded_date="2025-04-16"
        )

        self.book3 = Book.objects.create(
            book_name="Another History Book",
            book_author="Author 3",
            book_barcode="123456787",
            book_type="History",
            category=self.category1,
            book_rating_avg=5.0,
            book_reading_counter=150,
            book_favourite_counter=70,
            status=Book.Status.PENDING,
            book_uploaded_date="2025-04-15"
        )

    def test_search_by_name(self):
        """
        Test tìm kiếm theo tên sách
        Mã Test: UT-BSV-01
        Input:
        - Query param search="History"
        Expected Output:
        - Trả về 1 sách tên "Test History Book"
        - Status code 200
        """
        url = '/search/?search=History'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only return accepted books
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_filter_by_category(self):
        """
        Test lọc theo category
        Mã Test: UT-BSV-02
        Input:
        - Query param category=<ID category 2>
        Expected Output:
        - Trả về 1 sách thuộc category "Sport"
        """
        url = f'/search/?category={self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test Sport Book")  
          
    def test_filter_by_rating(self):
        """
        Test lọc theo rating
        Mã Test: UT-BSV-03
        Input:
        - Query param min_rating=4
        Expected Output:
        - Trả về sách có rating >= 4
        """
        url = '/search/?min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(float(response.data['results'][0]['book_rating_avg']), 4.0)

    def test_sort_by_most_reviewed(self):
        """
        Test sắp xếp theo số lượt đọc
        Mã Test: UT-BSV-04
        Input:
        - Query param sort_by=reviewed
        Expected Output:
        - Danh sách sách được sắp xếp giảm dần theo book_reading_counter
        """
        url = '/search/?sort_by=reviewed'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_reading_counter'] >= results[i+1]['book_reading_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_favourite(self):
        """
        Test sắp xếp theo lượt yêu thích
        Mã Test: UT-BSV-05
        Input:
        - Query param sort_by=favourite
        Expected Output:
        - Danh sách sách được sắp xếp giảm dần theo book_favourite_counter
        """
        url = '/search/?sort_by=favourite'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_favourite_counter'] >= results[i+1]['book_favourite_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_newest(self):
        """
        Test sắp xếp theo ngày upload
        Mã Test: UT-BSV-06
        Input:
        - Query param sort_by=newest
        Expected Output:
        - Danh sách sách được sắp xếp giảm dần theo book_uploaded_date
        """
        url = '/search/?sort_by=newest'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_uploaded_date'] >= results[i+1]['book_uploaded_date'] 
                          for i in range(len(results)-1)))

    def test_multiple_filters(self):
        """
        Test lọc kết hợp nhiều tiêu chí
        Mã Test: UT-BSV-07
        Input:
        - search=History, category=<ID category1>, min_rating=4
        Expected Output:
        - Trả về đúng sách "Test History Book"
        """
        url = f'/search/?search=History&category={self.category1.category_id}&min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_empty_search(self):
        """
        Test khi không truyền query
        Mã Test: UT-BSV-08
        Input:
        - Không truyền search, category, rating...
        Expected Output:
        - Trả về toàn bộ sách đã ACCEPTED
        """
        url = '/search/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only accepted books

    def test_pagination(self):
        """
        Test phân trang kết quả
        Mã Test: UT-BSV-09
        Input:
        - Tạo thêm sách để vượt giới hạn trang
        Expected Output:
        - Trả về trang đầu tiên có 4 kết quả
        - Có trường 'next', 'previous'
        """
        # Create additional books to test pagination
        for i in range(5):
            Book.objects.create(
                book_name=f"Test Book {i}",
                book_author=f"Author {i}",
                book_type="History",
                book_barcode=f"TEST{i}",
                category=self.category1,
                status=Book.Status.ACCEPTED,
                book_uploaded_date=now()
            )
            
        url = '/search/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertEqual(len(response.data['results']), 4)  # Default page size is 4

    def test_multiple_categories(self):
        """
        Test lọc nhiều category
        Mã Test: UT-BSV-10
        Input:
        - category=<ID1>,<ID2>
        Expected Output:
        - Trả về sách thuộc cả hai category
        """
        url = f'/search/?category={self.category1.category_id},{self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_invalid_rating_filter(self):
        """
        Test lọc với giá trị rating không hợp lệ
        Mã Test: UT-BSV-11
        Input:
        - Các giá trị min_rating: 'invalid', -1, 6, 'abc123'
        Expected Output:
        - Trả về status 400 và thông báo lỗi dạng chuỗi
        """
        test_cases = [
            'invalid',  # Chuỗi không phải số
            '-1',      # Số âm
            '6',       # Số lớn hơn 5 
            'abc123'   # Ký tự hỗn hợp
        ]
        
        for invalid_rating in test_cases:
            url = f'/search/?min_rating={invalid_rating}'
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertTrue(isinstance(response.data['error'], str))  # Đảm bảo error message là chuỗi