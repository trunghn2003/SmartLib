from unittest import mock
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.utils.timezone import now
import bcrypt
from .models import User, Reader, Gamification_Record, Notification, Book, Rating_And_Review, Category, Manager
from .views import AddRatingAndReviewView, UserLoginView, send_another_email, send_verification_email_register, token_generator_register
from unittest.mock import MagicMock, patch, PropertyMock, ANY
import datetime, jwt
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Incorrect password!")

    def test_user_not_found(self):
        """Test login with non-existent user
        Mã Test: UT-ULV-03"""
        data = {
            'email': 'nonexistent@example.com',
            'user_password': 'testpass123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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
        """Test token with non-existent user ID"""
        data = {'token': self.nonexistent_user_token}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "User not found!")

    """Mã Test: UT-RTV-05"""
    def test_expired_token_explicit(self):
        """Test explicit handling of expired token"""
        data = {'token': self.expired_token}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Token has expired!")

    """Mã Test: UT-RTV-06"""
    def test_malformed_token(self):
        """Test with malformed token"""
        data = {'token': 'malformed.token.here'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Invalid token!")

    """Mã Test: UT-RTV-07"""
    def test_empty_token(self):
        """Test with empty token string"""
        data = {'token': ''}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Token is required!")


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
        )

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
            book_type="History",
            category=self.category1,
            book_rating_avg=5.0,
            book_reading_counter=150,
            book_favourite_counter=70,
            status=Book.Status.PENDING,
            book_uploaded_date="2025-04-15"
        )

    def test_search_by_name(self):
        """Test searching books by name"""
        url = '/search/?search=History'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only return accepted books
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_filter_by_category(self):
        """Test filtering books by category"""
        url = f'/search/?category={self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test Sport Book")

    def test_filter_by_rating(self):
        """Test filtering books by minimum rating"""
        url = '/search/?min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_rating_avg'], 4.5)

    def test_sort_by_most_reviewed(self):
        """Test sorting books by review count"""
        url = '/search/?sort_by=reviewed'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_reading_counter'] >= results[i+1]['book_reading_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_favourite(self):
        """Test sorting books by favourite count"""
        url = '/search/?sort_by=favourite'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_favourite_counter'] >= results[i+1]['book_favourite_counter'] 
                          for i in range(len(results)-1)))

    def test_sort_by_newest(self):
        """Test sorting books by upload date"""
        url = '/search/?sort_by=newest'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(results[i]['book_uploaded_date'] >= results[i+1]['book_uploaded_date'] 
                          for i in range(len(results)-1)))

    def test_multiple_filters(self):
        """Test combining multiple search filters"""
        url = f'/search/?search=History&category={self.category1.category_id}&min_rating=4'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book_name'], "Test History Book")

    def test_empty_search(self):
        """Test search with no parameters returns all accepted books"""
        url = '/search/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only accepted books

    def test_pagination(self):
        """Test search results pagination"""
        # Create additional books to test pagination
        for i in range(5):
            Book.objects.create(
                book_name=f"Test Book {i}",
                book_author=f"Author {i}",
                book_type="History",
                category=self.category1,
                status=Book.Status.ACCEPTED
            )
            
        url = '/search/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertEqual(len(response.data['results']), 4)  # Default page size is 4

    def test_multiple_categories(self):
        """Test filtering by multiple categories"""
        url = f'/search/?category={self.category1.category_id},{self.category2.category_id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_invalid_rating_filter(self):
        """Test invalid rating filter value"""
        url = '/search/?min_rating=invalid'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should ignore invalid rating and return all accepted books
        self.assertEqual(len(response.data['results']), 2)

