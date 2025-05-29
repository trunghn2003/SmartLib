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

class UserLoginViewTest(APITestCase):
    """Test cases for UserLoginView"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.url = reverse('login-api')
        
        # Create a test user
        password = "testpass123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password=hashed_password,
            is_active=True
        )
        
        # Create associated reader
        self.reader = Reader.objects.create(
            user=self.user,
            reader_rank="Rookie",
            reader_point=0
        )

    def test_successful_login(self):
        """Test successful login with correct credentials
        Mã Test: UT-ULV-01"""
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)
        self.assertIn('isDailyLogin', response.data)

    def test_incorrect_password(self):
        """Test login with incorrect password
        Mã Test: UT-ULV-02"""
        data = {
            'email': 'test@example.com',
            'user_password': 'wrongpassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Incorrect password!")

    def test_user_not_found(self):
        """Test login with non-existent user
        Mã Test: UT-ULV-03"""
        data = {
            'email': 'nonexistent@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "User not found or incorrect password!")

    def test_inactive_user(self):
        """Test login with inactive user account
        Mã Test: UT-ULV-04"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Your account has not activated yet.")

    def test_daily_login_points(self):
        """Test daily login point system
        Mã Test: UT-ULV-05"""
        # Set last login to yesterday
        self.user.last_login = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        self.user.save()
        
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isDailyLogin'])
        
        # Verify reader points were updated
        reader = Reader.objects.get(user=self.user)
        self.assertEqual(reader.reader_point, 10)

        # Verify gamification record was created
        gamification_record = Gamification_Record.objects.filter(
            reader=reader, 
            gamification_description="Daily login"
        ).first()
        self.assertIsNotNone(gamification_record)
        self.assertEqual(gamification_record.achieved_point, 10)

        # Verify notification was created
        notification = Notification.objects.filter(
            reader=reader,
            notification_title="New Point Achievement",
            notification_record="+10 Point for Daily login"
        ).first()
        self.assertIsNotNone(notification)

    def test_reader_rank_updates(self):
        """Test reader rank updates based on points
        Mã Test: UT-ULV-06"""
        # Initial state should be Rookie with 0 points
        self.assertEqual(self.reader.reader_rank, "Rookie")
        self.assertEqual(self.reader.reader_point, 0)
        
        # Test Bronze rank (500-1499 points)
        self.reader.reader_point = 490  # Just below Bronze
        self.reader.save()
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 500)
        self.assertEqual(self.reader.reader_rank, "Bronze")
        
        # Test Silver rank (1500-2999 points)
        self.reader.reader_point = 1490
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 1500)
        self.assertEqual(self.reader.reader_rank, "Silver")
        
        # Test Gold rank (3000+ points)
        self.reader.reader_point = 2990
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 3000)
        self.assertEqual(self.reader.reader_rank, "Gold")

    def test_reader_rank_boundaries(self):
        """Test reader rank boundary conditions
        Mã Test: UT-ULV-07"""
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        
        # Test just below Bronze boundary
        self.reader.reader_point = 499
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 509)
        self.assertEqual(self.reader.reader_rank, "Bronze")
        
        # Test just below Silver boundary
        self.reader.reader_point = 1499
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 1509)
        self.assertEqual(self.reader.reader_rank, "Silver")
        
        # Test just below Gold boundary
        self.reader.reader_point = 2999
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 3009)
        self.assertEqual(self.reader.reader_rank, "Gold")

        # Test well into Gold rank
        self.reader.reader_point = 3500
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 3510)
        self.assertEqual(self.reader.reader_rank, "Gold")

    def test_rank_transition_points(self):
        """Test rank transitions at exact point boundaries
        Mã Test: UT-ULV-08"""
        data = {
            'email': 'test@example.com',
            'user_password': 'testpass123'
        }
        
        # Test transition to Bronze rank at exactly 500 points
        self.reader.reader_point = 490
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 500)
        self.assertEqual(self.reader.reader_rank, "Bronze")
        
        # Test staying in Bronze rank between 500 and 1499
        self.reader.reader_point = 1000
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 1010)
        self.assertEqual(self.reader.reader_rank, "Bronze")
        
        # Test transition to Silver rank at exactly 1500 points
        self.reader.reader_point = 1490
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 1500)
        self.assertEqual(self.reader.reader_rank, "Silver")
        
        # Test staying in Silver rank between 1500 and 2999
        self.reader.reader_point = 2000
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 2010)
        self.assertEqual(self.reader.reader_rank, "Silver")
        
        # Test transition to Gold rank at exactly 3000 points
        self.reader.reader_point = 2990
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 3000)
        self.assertEqual(self.reader.reader_rank, "Gold")
        
        # Test staying in Gold rank above 3000
        self.reader.reader_point = 3500
        self.reader.save()
        response = self.client.post(self.url, data, format='json')
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.reader_point, 3510)
        self.assertEqual(self.reader.reader_rank, "Gold")


class RefreshTokenViewTest(APITestCase):
    """Test cases for RefreshTokenView"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.url = reverse('refresh-token-api')

        # Create a test user
        password = "testpass123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password=hashed_password,
            is_active=True
        )

        # Create valid token with specific payload
        payload = {
            'id': self.user.user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180),
            'iat': datetime.datetime.utcnow()
        }
        self.valid_token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Create expired token with specific expiration
        expired_payload = {
            'id': self.user.user_id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(minutes=190)
        }
        self.expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')

        # Create token with non-existent user ID
        nonexistent_payload = {
            'id': 99999,  # Non-existent user ID
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180),
            'iat': datetime.datetime.utcnow()
        }
        self.nonexistent_user_token = jwt.encode(nonexistent_payload, 'secret', algorithm='HS256')

    """Mã Test: UT-RTV-01"""
    def test_missing_token(self):
        """Test when token is not provided in request data"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Token is required!")

    """Mã Test: UT-RTV-02"""
    def test_valid_token_flow(self):
        """Test complete flow with valid token"""
        data = {'token': self.valid_token}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)

        # Verify new token is valid and contains correct data
        new_token = response.data['jwt']
        decoded = jwt.decode(new_token, 'secret', algorithms=['HS256'])
        self.assertEqual(decoded['id'], self.user.user_id)
        self.assertTrue('exp' in decoded)
        self.assertTrue('iat' in decoded)    
    """Mã Test: UT-RTV-03"""
    def test_inactive_user_token(self):
        """Test token refresh with inactive user"""
        # Deactivate the user
        self.user.is_active = False
        self.user.save()

        data = {'token': self.valid_token}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Your account is not active.")    
        """Mã Test: UT-RTV-04"""    
    def test_nonexistent_user_token(self):
        """Test token with non-existent user ID
        Mã Test: UT-RTV-04"""
        data = {'token': self.nonexistent_user_token}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "User not found!")

    """Mã Test: UT-RTV-05"""    
    def test_expired_token_explicit(self):
        """Test explicit handling of expired token
        Mã Test: UT-RTV-05"""
        data = {'token': self.expired_token}
        
        with self.assertRaises(AuthenticationFailed) as context:
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(str(context.exception), "Token has expired!")

    """Mã Test: UT-RTV-06"""    
    def test_malformed_token(self):
        """Test with malformed token
        Mã Test: UT-RTV-06"""
        data = {'token': 'malformed.token.here'}
        
        with self.assertRaises(AuthenticationFailed) as context:
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(str(context.exception), "Invalid token!")

    """Mã Test: UT-RTV-07"""
    def test_empty_token(self):
        """Test with empty token string
        Mã Test: UT-RTV-07"""
        data = {'token': ''}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Token is required!")    
    def test_expired_token_with_milliseconds(self):
        """Test expired token handling with millisecond precision
        Mã Test: UT-RTV-08"""
        # Create token that expired exactly at a millisecond boundary
        expired_payload = {
            'id': self.user.user_id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(microseconds=1),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(minutes=180)
        }
        just_expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')

        data = {'token': just_expired_token}
        
        with self.assertRaises(AuthenticationFailed) as context:
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(str(context.exception), "Token has expired!")

    def test_expired_token_edge_cases(self):
        """Test token expiration at edge cases
        Mã Test: UT-RTV-09"""
        # Test multiple expired scenarios
        test_cases = [
            datetime.timedelta(seconds=1),  # Just expired
            datetime.timedelta(minutes=1),  # Expired a minute ago
            datetime.timedelta(hours=1),    # Expired an hour ago
            datetime.timedelta(days=1),     # Expired a day ago
        ]

        for delta in test_cases:
            expired_payload = {
                'id': self.user.user_id,
                'exp': datetime.datetime.utcnow() - delta,
                'iat': datetime.datetime.utcnow() - datetime.timedelta(minutes=180)
            }
            expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')

            data = {'token': expired_token}
            
            with self.assertRaises(AuthenticationFailed) as context:
                response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(str(context.exception), "Token has expired!")

    def test_token_expiring_soon(self):
        """Mã Test: UT-RTV-10"""
        """Test token that is about to expire but hasn't yet"""
        # Create token that expires in 1 second
        payload = {
            'id': self.user.user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow()
        }
        expiring_soon_token = jwt.encode(payload, 'secret', algorithm='HS256')

        data = {'token': expiring_soon_token}
        response = self.client.post(self.url, data, format='json')

        # Should still be valid
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)


class EmailExistViewTest(APITestCase):
    """Test cases for EmailExistView"""

    def setUp(self):
        """Set up test data"""
        # Create a test user with hashed password
        self.user_email = "test@example.com"
        self.url = '/check-email-api'  # Updated URL pattern
        password = "testpass123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.user = User.objects.create(
            user_name="testuser",
            email=self.user_email,
            user_password=hashed_password,
            is_active=True
        )
        
    # Mã Test: UT-EEV-01
    def test_email_exists(self):
        """Test when email exists in the database"""
        data = {'email': self.user_email}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['exists'])
        self.assertEqual(response.data['message'], "Email is found.")

    # Mã Test: UT-EEV-02
    def test_email_does_not_exist(self):
        """Test when email does not exist in the database"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['exists'])
        self.assertEqual(response.data['message'], "Email not found.")
        
    # Mã Test: UT-EEV-03
    def test_empty_email(self):
        """Test when email is empty"""
        data = {'email': ''}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['exists'])
        self.assertEqual(response.data['message'], "Email not found.")

    # Mã Test: UT-EEV-04
    def test_invalid_email_format(self):
        """Test with invalid email format"""
        data = {'email': 'invalid-email-format'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['exists'])
        self.assertEqual(response.data['message'], "Email not found.")

    # Mã Test: UT-EEV-05
    def test_missing_email_field(self):
        """Test when email field is missing from request"""
        data = {}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['exists'])
        self.assertEqual(response.data['message'], "Email not found.")


class RegisterEmailVerificationTest(TestCase):
    """Test cases for email verification during registration"""
    
    def setUp(self):
        """Set up test environment"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        
        # Create test user
        password = "testpass123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password=hashed_password,
            is_active=False
        )    # Mã Test: UT-REV-01
    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_send_verification_email_success(self, mock_email):
        """Kiểm tra gửi email xác thực thành công"""
        send_verification_email_register(self.user, self.request)
        
        # Verify email was constructed correctly
        mock_email.assert_called_once_with(
            'Activate your account.',
            mock.ANY,
            settings.EMAIL_HOST_USER,
            [self.user.email]
        )
        
        # Verify email was sent
        mock_email_instance = mock_email.return_value
        mock_email_instance.send.assert_called_once()    # Mã Test: UT-REV-02
    @patch('smartlib_api.views.render_to_string')
    def test_email_template_context(self, mock_render):
        """Kiểm tra tạo context cho template email"""
        send_verification_email_register(self.user, self.request)
        
        # Verify template context
        mock_render.assert_called_once()
        context = mock_render.call_args[0][1]
        
        self.assertEqual(context['user'], self.user)
        self.assertEqual(context['domain'], self.request.get_host())
        self.assertEqual(context['user_name'], self.user.user_name)
        self.assertIn('uid', context)
        self.assertIn('token', context)    # Mã Test: UT-REV-03
    def test_uid_generation(self):
        """Kiểm tra quá trình tạo UID cho xác thực email"""
        with patch('smartlib_api.views.urlsafe_base64_encode') as mock_encode:
            mock_encode.return_value = 'test-uid'
            
            send_verification_email_register(self.user, self.request)
            
            # Verify UID generation
            mock_encode.assert_called_once()
            args = mock_encode.call_args[0][0]
            self.assertEqual(int(force_str(args)), self.user.pk)    # Mã Test: UT-REV-04
    def test_token_generation(self):
        """Kiểm tra quá trình tạo token cho xác thực email"""
        with patch('smartlib_api.views.token_generator_register') as mock_generator:
            mock_generator.make_token.return_value = 'test-token'
            
            send_verification_email_register(self.user, self.request)
            
            # Verify token generation
            mock_generator.make_token.assert_called_once_with(self.user)    # Mã Test: UT-REV-05
    def test_template_rendering(self):
        """Kiểm tra quá trình render template email"""
        with patch('smartlib_api.views.render_to_string') as mock_render:
            mock_render.return_value = 'rendered template'
            
            send_verification_email_register(self.user, self.request)
            
            # Verify template rendering
            mock_render.assert_called_once_with(
                '4_2_email_templet_register.html',
                mock.ANY
            )    # Mã Test: UT-REV-06
    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_email_alternative_content(self, mock_email):
        """Kiểm tra đính kèm nội dung HTML thay thế"""
        send_verification_email_register(self.user, self.request)
        
        # Verify HTML content was attached
        mock_email_instance = mock_email.return_value
        mock_email_instance.attach_alternative.assert_called_once_with(
            mock.ANY,
            'text/html'
        )

    # Mã Test: UT-REV-07
    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_email_sending_failure(self, mock_email):
        """Test email sending failure handling"""
        mock_email_instance = mock_email.return_value
        mock_email_instance.send.side_effect = Exception("Email sending failed")
        
        with self.assertRaises(Exception) as context:
            send_verification_email_register(self.user, self.request)
        
        self.assertTrue("Email sending failed" in str(context.exception))

    # Mã Test: UT-REV-08
    @patch('smartlib_api.views.render_to_string')
    def test_template_rendering_failure(self, mock_render):
        """Test template rendering failure handling"""
        mock_render.side_effect = Exception("Template rendering failed")
        
        with self.assertRaises(Exception) as context:
            send_verification_email_register(self.user, self.request)
        
        self.assertTrue("Template rendering failed" in str(context.exception))

    # Mã Test: UT-REV-09
    def test_email_subject(self):
        """Test email subject generation"""
        with patch('smartlib_api.views.EmailMultiAlternatives') as mock_email:
            send_verification_email_register(self.user, self.request)
            
            # Verify email subject
            args = mock_email.call_args[0]
            self.assertEqual(args[0], 'Activate your account.')

    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_send_verification_email_success(self, mock_email):
        """Test successful email verification sending"""
        send_verification_email_register(self.user, self.request)
        
        # Verify email was created with correct parameters
        mock_email.assert_called_once()
        call_args = mock_email.call_args[0]
        
        self.assertEqual(call_args[0], 'Activate your account.')  # Check subject
        self.assertEqual(call_args[2], settings.EMAIL_HOST_USER)  # Check sender
        self.assertEqual(call_args[3], [self.user.email])  # Check recipient
        
        # Verify email methods were called
        mock_email_instance = mock_email.return_value
        mock_email_instance.attach_alternative.assert_called_once()
        mock_email_instance.send.assert_called_once()

    @patch('smartlib_api.views.render_to_string')
    def test_email_template_context(self, mock_render):
        """Test email template context data"""
        send_verification_email_register(self.user, self.request)
        
        # Verify template context
        context = mock_render.call_args[0][1]
        self.assertEqual(context['user'], self.user)
        self.assertEqual(context['domain'], self.request.get_host())
        self.assertEqual(context['user_name'], self.user.user_name)
        self.assertTrue('uid' in context)
        self.assertTrue('token' in context)

    def test_uid_token_validity(self):
        """Test UID and token generation"""
        # Generate UID and token
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = token_generator_register.make_token(self.user)
        
        # Verify UID decoding
        decoded_uid = force_str(urlsafe_base64_decode(uid))
        self.assertEqual(int(decoded_uid), self.user.pk)
        
        # Verify token validity
        self.assertTrue(token_generator_register.check_token(self.user, token))

    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_email_sending_error(self, mock_email):
        """Test email sending error handling"""
        mock_email_instance = mock_email.return_value
        mock_email_instance.send.side_effect = Exception("Email sending failed")
        
        with self.assertRaises(Exception) as context:
            send_verification_email_register(self.user, self.request)
        
        self.assertTrue("Email sending failed" in str(context.exception))

    def test_resend_verification_email(self):
        """Test resending verification email"""
        response = self.client.get(f'/send-another-email/{self.user.email}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Verification email sent successfully.')

    def test_resend_to_nonexistent_email(self):
        """Test resending to non-existent email"""
        response = self.client.get('/send-another-email/nonexistent@example.com/')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'User with the provided email does not exist.')

    @patch('smartlib_api.views.render_to_string')
    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_template_rendering_error(self, mock_email, mock_render):
        """Test template rendering error handling"""
        mock_render.side_effect = Exception("Template rendering failed")
        
        with self.assertRaises(Exception) as context:
            send_verification_email_register(self.user, self.request)
        
        self.assertTrue("Template rendering failed" in str(context.exception))
        mock_email.assert_not_called()

    @patch('smartlib_api.views.settings')
    def test_email_host_configuration(self, mock_settings):
        """Test email host configuration"""
        mock_settings.EMAIL_HOST_USER = 'test@host.com'
        send_verification_email_register(self.user, self.request)
        self.assertEqual(mock_settings.EMAIL_HOST_USER, 'test@host.com')

    @patch('smartlib_api.views.EmailMultiAlternatives')
    def test_html_content_in_email(self, mock_email):
        """Test HTML content in email"""
        send_verification_email_register(self.user, self.request)
        
        mock_email_instance = mock_email.return_value
        mock_email_instance.attach_alternative.assert_called_once()
        call_args = mock_email_instance.attach_alternative.call_args[0]
        self.assertEqual(call_args[1], 'text/html')

    @patch('smartlib_api.views.token_generator_register')
    def test_token_expiration(self, mock_token_generator):
        """Test token expiration after 30 minutes"""
        # Generate token
        mock_token_generator.make_token.return_value = 'test_token'
        token = mock_token_generator.make_token(self.user)
        
        # Simulate time passing
        mock_token_generator.check_token.return_value = False
        
        # Verify token expiration
        self.assertFalse(mock_token_generator.check_token(self.user, token))

    @patch('smartlib_api.views.urlsafe_base64_encode')
    def test_uid_encoding_error(self, mock_encode):
        """Test UID encoding error handling"""
        mock_encode.side_effect = Exception("UID encoding failed")
        
        with self.assertRaises(Exception) as context:
            send_verification_email_register(self.user, self.request)
        
        self.assertTrue("UID encoding failed" in str(context.exception))

    def test_specific_email_content_verification(self):
        """Test specific email content and construction"""
        with patch('smartlib_api.views.EmailMultiAlternatives') as mock_email:
            send_verification_email_register(self.user, self.request)
            
            # Check email construction matches highlighted lines
            mock_email.assert_called_once_with(
                'Activate your account.',  # Line 324
                mock.ANY,  # message content
                settings.EMAIL_HOST_USER,  # Line 336
                [self.user.email],  # Line 337
            )
            
            # Verify HTML alternative attachment
            mock_email_instance = mock_email.return_value
            mock_email_instance.attach_alternative.assert_called_once_with(
                mock.ANY,  # message content
                "text/html"  # Line 339
            )
            mock_email_instance.send.assert_called_once()  # Line 340

    def test_token_generation_specifics(self):
        """Test specific token generation process"""
        with patch('smartlib_api.views.token_generator_register') as mock_generator:
            mock_generator.make_token.return_value = 'test_token'
            
            send_verification_email_register(self.user, self.request)
            
            # Verify token generator is called with user
            mock_generator.make_token.assert_called_once_with(self.user)  # Line 322

    def test_uid_encoding_specifics(self):
        """Test specific UID encoding process"""
        with patch('smartlib_api.views.urlsafe_base64_encode') as mock_encode:
            with patch('smartlib_api.views.force_bytes') as mock_force_bytes:
                send_verification_email_register(self.user, self.request)
                
                # Verify force_bytes is called with user.pk
                mock_force_bytes.assert_called_once_with(self.user.pk)  # Line 321
                # Verify urlsafe_base64_encode is called with force_bytes result
                mock_encode.assert_called_once_with(mock_force_bytes.return_value)

    def test_template_rendering_specifics(self):
        """Test specific template rendering process"""
        with patch('smartlib_api.views.render_to_string') as mock_render:
            send_verification_email_register(self.user, self.request)
            
            # Verify template name and context
            mock_render.assert_called_once_with(
                '4_2_email_templet_register.html',  # Line 325
                {
                    'user': self.user,
                    'domain': self.request.get_host(),
                    'uid': mock.ANY,
                    'token': mock.ANY,
                    'user_name': self.user.user_name,
                }
            )

    def test_token_timestamp_check(self):
        """Test token timestamp verification
        Mã Test: UT-REV-10"""
        # Create a token with custom timestamp
        timestamp = str(int(timezone.now().timestamp()))
        base_token = super(token_generator_register, token_generator_register).make_token(self.user)
        token = f"{base_token}-{timestamp}"

        # Test valid token
        self.assertTrue(token_generator_register.check_token(self.user, token))

        # Test expired token
        expired_timestamp = str(int((timezone.now() - datetime.timedelta(minutes=31)).timestamp()))
        expired_token = f"{base_token}-{expired_timestamp}"
        self.assertFalse(token_generator_register.check_token(self.user, expired_token))

    def test_token_format_validation(self):
        """Test token format validation
        Mã Test: UT-REV-11"""
        # Test malformed token (no timestamp)
        malformed_token = "invalid-token"
        self.assertFalse(token_generator_register.check_token(self.user, malformed_token))

        # Test malformed timestamp
        base_token = super(token_generator_register, token_generator_register).make_token(self.user)
        invalid_timestamp_token = f"{base_token}-notanumber"
        self.assertFalse(token_generator_register.check_token(self.user, invalid_timestamp_token))

        # Test token with missing parts
        incomplete_token = "only-one-part"
        self.assertFalse(token_generator_register.check_token(self.user, incomplete_token))

        # Test empty token
        self.assertFalse(token_generator_register.check_token(self.user, ""))

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
        """Mã Test: UT-BSV-01"""
        """Test searching books by name"""
        url = '/search/?search=History'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only return accepted books
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_filter_by_category(self):
        """Mã Test: UT-BSV-02"""
        """Test filtering books by category"""
        url = f'/search/?category={self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test Sport Book")  
          
    def test_filter_by_rating(self):
        """Mã Test: UT-BSV-03"""
        """Test filtering books by minimum rating"""
        url = '/search/?min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(float(response.data['results'][0]['book_rating_avg']), 4.0)

    def test_sort_by_most_reviewed(self):
        """Mã Test: UT-BSV-04"""
        """Test sorting books by review count"""
        url = '/search/?sort_by=reviewed'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_reading_counter'] >= results[i+1]['book_reading_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_favourite(self):
        """Mã Test: UT-BSV-05"""
        """Test sorting books by favourite count"""
        url = '/search/?sort_by=favourite'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_favourite_counter'] >= results[i+1]['book_favourite_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_newest(self):
        """Mã Test: UT-BSV-06"""
        """Test sorting books by upload date"""
        url = '/search/?sort_by=newest'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_uploaded_date'] >= results[i+1]['book_uploaded_date'] 
                          for i in range(len(results)-1)))

    def test_multiple_filters(self):
        """Mã Test: UT-BSV-07"""
        """Test combining multiple search filters"""
        url = f'/search/?search=History&category={self.category1.category_id}&min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_empty_search(self):
        """Mã Test: UT-BSV-08"""
        """Test search with no parameters returns all accepted books"""
        url = '/search/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only accepted books

    def test_pagination(self):
        """Mã Test: UT-BSV-09"""
        """Test search results pagination"""
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
        """Mã Test: UT-BSV-10"""
        """Test filtering by multiple categories"""
        url = f'/search/?category={self.category1.category_id},{self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_invalid_rating_filter(self):
        """Mã Test: UT-BSV-11"""
        """Kiểm tra xử lý khi giá trị filter rating không hợp lệ"""
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

class SendAnotherEmailTest(TestCase):
    """Test cases for send_another_email function"""

    def setUp(self):
        """Set up test environment"""
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        
        # Create test user
        password = "testpass123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password=hashed_password,
            is_active=False
        )

    # Mã Test: UT-SAE-01
    @patch('smartlib_api.views.send_verification_email_register')
    def test_send_another_email_success(self, mock_send_email):
        """Kiểm tra gửi lại email xác thực thành công"""
        response = send_another_email(self.request, self.user.email)
        
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Verification email sent successfully.')
        
        # Verify send_verification_email_register was called
        mock_send_email.assert_called_once_with(self.user, self.request)

    # Mã Test: UT-SAE-02
    def test_send_another_email_nonexistent_user(self):
        """Kiểm tra trường hợp email không tồn tại trong hệ thống"""
        response = send_another_email(self.request, 'nonexistent@example.com')
        
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'User with the provided email does not exist.')

    # Mã Test: UT-SAE-03
    @patch('smartlib_api.views.send_verification_email_register')
    def test_send_another_email_error_handling(self, mock_send_email):
        """Kiểm tra xử lý lỗi khi gửi email"""
        # Simulate email sending failure
        mock_send_email.side_effect = Exception("Email sending failed")
        
        with self.assertRaises(Exception) as context:
            send_another_email(self.request, self.user.email)
        
        self.assertTrue("Email sending failed" in str(context.exception))

    # Mã Test: UT-SAE-04
    def test_send_another_email_invalid_email_format(self):
        """Kiểm tra trường hợp định dạng email không hợp lệ"""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test@.com',
            'test@example.'
        ]
        
        for email in invalid_emails:
            response = send_another_email(self.request, email)
            data = json.loads(response.content)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['error'], 'User with the provided email does not exist.')

    # Mã Test: UT-SAE-05
    def test_send_another_email_empty_email(self):
        """Kiểm tra trường hợp email trống"""
        response = send_another_email(self.request, '')
        
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], 'User with the provided email does not exist.')

    # Mã Test: UT-SAE-06
    @patch('smartlib_api.views.send_verification_email_register')
    def test_send_another_email_multiple_requests(self, mock_send_email):
        """Kiểm tra gửi nhiều lần email xác thực"""
        # Send multiple requests
        for _ in range(3):
            response = send_another_email(self.request, self.user.email)
            data = json.loads(response.content)
            self.assertEqual(response.status_code, 200)  
            self.assertEqual(data['message'], 'Verification email sent successfully.')
        
        # Verify send_verification_email_register was called multiple times
        self.assertEqual(mock_send_email.call_count, 3)

class AddBookTest(APITestCase):
    """Test cases for add_book function"""

    def setUp(self):
        """Set up test environment"""
        self.client = APIClient()
        self.url = '/add-book/'
        
        # Create test category
        self.category = Category.objects.create(category_name="Test Category")
        
        # Create test reader
        self.reader = Reader.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password="hashedpassword",
            reader_rank="BRONZE",
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
        """Test successful book addition
        Mã Test: UT-AB-01"""
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
        self.assertRegex(book.book_file.name, rf"{book.book_id}_file\\.pdf$")
        self.assertRegex(book.book_image.name, rf"{book.book_id}_image\\.jpg$")

    def test_request_method_validation(self):
        """Test method validation
        Mã Test: UT-AB-02"""
        # Test GET method
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['message'], 'Invalid request method.')

        # Test PUT method
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['message'], 'Invalid request method.')

    def test_required_fields_validation(self):
        """Test required fields validation
        Mã Test: UT-AB-03"""
        required_fields = ['title', 'author', 'barcode', 'description', 'category', 'bookfile', 'reader_id']
        
        for field in required_fields:
            # Create data without required field
            data = self.valid_data.copy()
            data.pop(field)
            
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()['status'], 'error')

    def test_invalid_category_validation(self):
        """Test category validation
        Mã Test: UT-AB-04"""
        # Test with non-existent category ID
        data = self.valid_data.copy()
        data['category'] = 99999
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid category.')

        # Test with invalid category ID type
        data['category'] = 'invalid'
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid category.')

    def test_file_handling_and_naming(self):
        """Test file upload and naming
        Mã Test: UT-AB-05"""
        response = self.client.post(self.url, self.valid_data, format='multipart')
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get(book_name=self.valid_data['title'])

        # Test file naming convention
        self.assertRegex(book.book_file.name, rf"{book.book_id}_file\\.pdf$")
        self.assertRegex(book.book_image.name, rf"{book.book_id}_image\\.jpg$")

        # Test optional image
        data = self.valid_data.copy()
        data.pop('bookImage')
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get(book_id=response.json()['book_id'])
        self.assertTrue(book.book_file)
        self.assertFalse(bool(book.book_image))

    def test_reader_points_and_rank_update(self):
        """Test reader points and rank update
        Mã Test: UT-AB-06"""
        test_cases = [
            (0, 50, "Bronze"),  # Initial
            (480, 530, "Bronze"),  # Enter Bronze
            (1480, 1530, "Silver"),  # Enter Silver
            (2980, 3030, "Gold"),  # Enter Gold
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

    def test_associated_records_creation(self):
        """Test creation of associated records
        Mã Test: UT-AB-07"""
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

    def test_duplicate_book_handling(self):
        """Test handling duplicate book uploads
        Mã Test: UT-AB-08"""
        # First upload should succeed
        response = self.client.post(self.url, self.valid_data, format='multipart')
        self.assertEqual(response.status_code, 200)

        # Upload same book again
        response = self.client.post(self.url, self.valid_data, format='multipart')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['status'], 'error')

    def test_invalid_reader_handling(self):
        """Test handling invalid reader
        Mã Test: UT-AB-09"""
        data = self.valid_data.copy()
        data['reader_id'] = 99999  # Non-existent reader

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['status'], 'error')

    def test_invalid_book_file(self):
        """Test invalid book file upload
        Mã Test: UT-AB-10"""
        data = self.valid_data.copy()
        data['bookfile'] = SimpleUploadedFile(
            "invalid_file.txt",
            b"invalid content",
            content_type="text/plain"
        )

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid file type.')

    def test_missing_book_file(self):
        """Test missing book file
        Mã Test: UT-AB-11"""
        data = self.valid_data.copy()
        data.pop('bookfile')

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Book file is required.')

    def test_invalid_book_image(self):
        """Test invalid book image upload
        Mã Test: UT-AB-12"""
        data = self.valid_data.copy()
        data['bookImage'] = SimpleUploadedFile(
            "invalid_image.txt",
            b"invalid content",
            content_type="text/plain"
        )

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid image type.')

    def test_missing_reader_id(self):
        """Test missing reader ID
        Mã Test: UT-AB-13"""
        data = self.valid_data.copy()
        data.pop('reader_id')

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Reader ID is required.')

    def tearDown(self):
        """Clean up after tests"""
        # Clean up files
        for book in Book.objects.all():
            if book.book_file:
                if hasattr(book.book_file.storage, 'delete'):
                    book.book_file.storage.delete(book.book_file.name)
            if book.book_image:
                if hasattr(book.book_image.storage, 'delete'):
                    book.book_image.storage.delete(book.book_image.name)

class BookInfoListViewTest(APITestCase):
    """Test cases for BookInfoListView"""
    def setUp(self):
        """Set up test data
        Khởi tạo dữ liệu test"""
        self.client = APIClient()
        self.category = Category.objects.create(
            category_name="Test Category"
        )
        
        # Create test book with all fields
        self.book = Book.objects.create(
            book_name="Test Book", 
            book_author="Test Author",
            book_barcode="123456789",
            book_type="Test",
            book_description="Test Description",
            category=self.category,
            book_reading_counter=0,
            book_rating_avg=0,
            book_favourite_counter=0,
            status=Book.Status.ACCEPTED,
            book_uploaded_date=now()
        )        # Base URL for book info
        self.url = '/get-book-info/'
        
    def test_get_book_info_success(self):
        """Test successful book info retrieval
        Mã Test: UT-BIV-01
        Test case này kiểm tra việc lấy thông tin sách thành công với book_id hợp lệ
        Input: 
        - book_id của sách đã tạo trong setUp
        Expected Output:
        - Status code: 200
        - Response data chứa đầy đủ và chính xác thông tin của sách"""

        url = f"{self.url}?book_id={self.book.book_id}"
        response = self.client.get(url)
        
        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify all book details
        self.assertEqual(data['book_name'], self.book.book_name)
        self.assertEqual(data['book_author'], self.book.book_author)
        self.assertEqual(data['book_barcode'], self.book.book_barcode)
        self.assertEqual(data['book_type'], self.book.book_type)
        self.assertEqual(data['book_description'], self.book.book_description)
        self.assertEqual(data['book_reading_counter'], self.book.book_reading_counter)
        self.assertEqual(data['book_rating_avg'], self.book.book_rating_avg)
        self.assertEqual(data['book_favourite_counter'], self.book.book_favourite_counter)
        self.assertEqual(data['status'], self.book.status)
        
    def test_get_book_info_nonexistent(self):
        """Test book info retrieval for non-existent book
        Mã Test: UT-BIV-02
        Test case này kiểm tra việc lấy thông tin sách với book_id không tồn tại
        Input:
        - book_id không tồn tại (99999) 
        Expected Output:
        - Status code: 400 BAD REQUEST
        - Error message: 'Book not found'"""

        url = f"{self.url}?book_id=99999"
        response = self.client.get(url)
        
        # Should return 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')

    def test_get_book_info_missing_id(self):
        """Test book info retrieval without book_id parameter
        Mã Test: UT-BIV-03
        Test case này kiểm tra việc gọi API mà không truyền book_id parameter
        Input:
        - Không có book_id parameter
        Expected Output:
        - Status code: 400 BAD REQUEST
        - Error message: 'Book not found'"""
        
        # Make request without book_id parameter
        response = self.client.get(self.url)
        
        # Should return 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')

    def test_get_book_info_invalid_id(self):
        """Test book info retrieval with invalid book_id format
        Mã Test: UT-BIV-04
        Test case này kiểm tra việc gọi API với book_id có format không hợp lệ
        Input:
        - book_id không hợp lệ: chữ cái, ký tự đặc biệt, số thập phân, số âm, None
        Expected Output:
        - Status code: 400 BAD REQUEST 

        - Error message: 'Book not found'"""

        invalid_ids = ['abc', '!@#', '1.23', '-1', 'None']
        for invalid_id in invalid_ids:
            url = f"{self.url}?book_id={invalid_id}"
            response = self.client.get(url)
            
            # Should return 400 status code
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json()['error'], 'Book not found')   
    def test_get_book_info_empty_id(self):
        """Test book info retrieval with empty book_id
        Mã Test: UT-BIV-05
        Test case này kiểm tra việc gọi API với book_id rỗng
        Input: 
        - book_id là chuỗi rỗng
        Expected Output:
        - Status code: 400 BAD REQUEST
        - Error message: 'Book not found'"""

        url = f"{self.url}?book_id="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')
    
        def test_get_book_info_with_deleted_book(self):
            """Test book info retrieval for a book that was deleted
        Mã Test: UT-BIV-06
        Test case này kiểm tra việc lấy thông tin sách đã bị xóa
        Input:
        - book_id của một sách đã được tạo và sau đó bị xóa khỏi database
        Expected Output:
        - Status code: 400 BAD REQUEST
        - Error message: 'Book not found'"""
        
        # Create and then delete a book
        book = Book.objects.create(
            book_name="To be deleted",
            book_author="Test Author",
            book_type="Test",
            book_barcode="987654321",
            category=self.category
        )
        book_id = book.book_id
        book.delete()

        url = f"{self.url}?book_id={book_id}"
        response = self.client.get(url)
        
        # Should return 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')

    def test_get_book_info_repeated_requests(self):
        """Test multiple requests for the same book info
        Mã Test: UT-BIV-07
        Test case này kiểm tra việc gọi API nhiều lần cho cùng một sách
        Input:
        - book_id của sách hợp lệ
        - Gọi API 3 lần liên tiếp
        Expected Output:
        - Cả 3 lần đều trả về:
            + Status code: 200
            + Response data giống nhau và chính xác"""
        
        url = f"{self.url}?book_id={self.book.book_id}"
        
        # Make 3 consecutive requests
        for _ in range(3):
            response = self.client.get(url)
            
            # Each request should return same valid response
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            
            # Verify essential book details each time
            self.assertEqual(data['book_name'], self.book.book_name)
            self.assertEqual(data['book_author'], self.book.book_author)
            self.assertEqual(data['status'], self.book.status)

class LoginPageViewTests(TestCase):
    """Test cases for loginPage view function
    Test IDs: UT-LPV-01 through UT-LPV-04"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse('loginPage')
        
    def test_login_page_renders_correct_template(self):
        """Test that loginPage view renders the correct template
        Test ID: UT-LPV-01"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '2_login_page.html')
        
    def test_login_page_get_method(self):
        """Test that loginPage view accepts GET requests
        Test ID: UT-LPV-02"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_login_page_post_method_not_allowed(self):
        """Test that loginPage view returns 405 for POST requests
        Test ID: UT-LPV-03"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
    def test_login_page_url_resolves(self):
        """Test that the login page URL resolves correctly
        Test ID: UT-LPV-04"""
        response = self.client.get('/login')  # Test the actual URL path
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '2_login_page.html')

class RegisterPageViewTests(TestCase):
    """Test cases for registerPage view function
    Test IDs: UT-RPV-01 through UT-RPV-04"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse('registerPage')
        
    def test_register_page_renders_correct_template(self):
        """Test that registerPage view renders the correct template
        Test ID: UT-RPV-01"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '3_register_page.html')
        
    def test_register_page_get_method(self):
        """Test that registerPage view accepts GET requests
        Test ID: UT-RPV-02"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_register_page_post_method_not_allowed(self):
        """Test that registerPage view returns 405 for POST requests
        Test ID: UT-RPV-03"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
    def test_register_page_url_resolves(self):
        """Test that the register page URL resolves correctly
        Test ID: UT-RPV-04"""
        response = self.client.get('/registerAccount')  # Test the actual URL path
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '3_register_page.html')

class BookInfoListViewTests(APITestCase):
    """Test cases for BookInfoListView API
    Test IDs: UT-BILV-01 through UT-BILV-07"""

    def setUp(self):
        """Set up test data"""
        # Create a test category
        self.category = Category.objects.create(
            category_name="Test Category"
        )
        
        # Create a test book with all required fields
        self.book = Book.objects.create(
            book_name="Test Book",
            book_author="Test Author",
            book_barcode="123456789",
            book_type="Test",
            book_description="Test Description",
            category=self.category,
            book_reading_counter=100,
            book_rating_avg=4.5,
            book_favourite_counter=50,
            status=Book.Status.ACCEPTED,
            book_uploaded_date=now()
        )
        
        # Base URL for book info endpoint
        self.url = '/get-book-info/'
        
    def test_get_book_info_success(self):
        """Test successful book info retrieval
        Test ID: UT-BILV-01"""
        url = f"{self.url}?book_id={self.book.book_id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify all book details are returned correctly
        self.assertEqual(data['book_name'], self.book.book_name)
        self.assertEqual(data['book_author'], self.book.book_author)
        self.assertEqual(data['book_barcode'], self.book.book_barcode)
        self.assertEqual(data['book_type'], self.book.book_type)
        self.assertEqual(data['book_description'], self.book.book_description)
        self.assertEqual(data['book_reading_counter'], self.book.book_reading_counter)
        self.assertEqual(float(data['book_rating_avg']), self.book.book_rating_avg)
        self.assertEqual(data['book_favourite_counter'], self.book.book_favourite_counter)
        self.assertEqual(data['status'], self.book.status)
        
    def test_get_book_info_nonexistent(self):
        """Test book info retrieval for non-existent book
        Test ID: UT-BILV-02"""
        url = f"{self.url}?book_id=99999"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')
        
    def test_get_book_info_missing_id(self):
        """Test book info retrieval without book_id parameter
        Test ID: UT-BILV-03"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')
        
    def test_get_book_info_invalid_id_format(self):
        """Test book info retrieval with invalid book_id format
        Test ID: UT-BILV-04"""
        invalid_ids = ['abc', '!@#', '1.23', '-1', 'None']
        for invalid_id in invalid_ids:
            url = f"{self.url}?book_id={invalid_id}"
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json()['error'], 'Book not found')
        
    def test_get_book_info_empty_id(self):
        """Test book info retrieval with empty book_id
        Test ID: UT-BILV-05"""
        url = f"{self.url}?book_id="
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')
    
    def test_get_book_info_deleted_book(self):
        """Test book info retrieval for a deleted book
        Test ID: UT-BILV-06"""
        # Create and then delete a book
        book = Book.objects.create(
            book_name="To be deleted",
            book_author="Test Author",
            book_type="Test",
            book_barcode="987654321",
            category=self.category
        )
        book_id = book.book_id
        book.delete()

        url = f"{self.url}?book_id={book_id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Book not found')
        
    def test_get_book_info_repeated_requests(self):
        """Test multiple sequential requests for the same book info
        Test ID: UT-BILV-07"""
        url = f"{self.url}?book_id={self.book.book_id}"
        
        # Make 3 consecutive requests
        for _ in range(3):
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.json()
            
            # Verify essential book details each time
            self.assertEqual(data['book_name'], self.book.book_name)
            self.assertEqual(data['book_author'], self.book.book_author)
            self.assertEqual(data['status'], self.book.status)

class ConfirmEmailRegisterViewTests(TestCase):
    """Test cases for confirm_email_register view function
    Test IDs: UT-CERV-01 through UT-CERV-04"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse('confirm_email_register')
        self.valid_email = 'test@example.com'
        
    def test_confirm_email_page_renders_correct_template(self):
        """Test that confirm_email_register view renders the correct template
        Test ID: UT-CERV-01"""
        response = self.client.get(f"{self.url}?email={self.valid_email}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '4_1_confirm_email_register_page.html')
        
    def test_confirm_email_with_valid_email(self):
        """Test confirm_email_register with valid email parameter
        Test ID: UT-CERV-02"""
        response = self.client.get(f"{self.url}?email={self.valid_email}")
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '4_1_confirm_email_register_page.html')
        self.assertEqual(response.context['email'], self.valid_email)
    
    def test_confirm_email_post_method_not_allowed(self):
        """Test that confirm_email_register view returns 405 for POST requests
        Test ID: UT-CERV-03"""
        response = self.client.post(f"{self.url}?email={self.valid_email}")
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

class FindAccountPageViewTests(TestCase):
    """Test cases for findAccountPage view function
    Test IDs: UT-FAPV-01 through UT-FAPV-04"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse('findAccountPage')
        
    def test_find_account_page_renders_correct_template(self):
        """Test that findAccountPage view renders the correct template
        Test ID: UT-FAPV-01"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '5_1_find_account_forgetPass_page.html')
        
    def test_find_account_page_get_method(self):
        """Test that findAccountPage view accepts GET requests
        Test ID: UT-FAPV-02"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_find_account_page_post_method_not_allowed(self):
        """Test that findAccountPage view returns 405 for POST requests
        Test ID: UT-FAPV-03"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
    def test_find_account_page_url_resolves(self):
        """Test that the find account page URL resolves correctly
        Test ID: UT-FAPV-04"""
        response = self.client.get('/find_account/')  # Test the actual URL path
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '5_1_find_account_forgetPass_page.html')

class ConfirmEmailChangePasswordTests(TestCase):
    """Test cases for confirm_email_change_password view function
    Test IDs: UT-CECP-01 through UT-CECP-04"""

    def setUp(self):
        """Set up test data"""
        self.url = reverse('confirm_email_change_password')
        
    def test_confirm_email_change_password_renders_correct_template(self):
        """Test that confirm_email_change_password view renders the correct template
        Test ID: UT-CECP-01"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '5_2_confirm_email_forgetPass_page.html')

        
    def test_confirm_email_change_password_with_valid_email(self):
        """Test confirm_email_change_password with valid email parameter
        Test ID: UT-CECP-02"""
        test_email = 'test@example.com'
        response = self.client.get(f"{self.url}?email={test_email}")
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '5_2_confirm_email_forgetPass_page.html')
        self.assertEqual(response.context['email'], test_email)
        
    def test_confirm_email_change_password_with_empty_email(self):
        """Test confirm_email_change_password with empty email parameter
        Test ID: UT-CECP-03"""
        response = self.client.get(f"{self.url}?email=")
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, '5_2_confirm_email_forgetPass_page.html')
        self.assertEqual(response.context['email'], '')
        
    def test_confirm_email_change_password_post_method_not_allowed(self):
        """Test that confirm_email_change_password view returns 405 for POST requests
        Test ID: UT-CECP-04"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

