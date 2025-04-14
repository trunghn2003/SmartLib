from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from django.utils.timezone import now
import bcrypt
from .models import User, Reader, Gamification_Record, Notification, Book, Rating_And_Review, Category, Manager, Preferences
from .views import AddRatingAndReviewView
from unittest.mock import patch, PropertyMock

# Create your tests here.

class GuestPageViewTests(TestCase):
    """
    Kiểm thử cho hàm guestPage
    """

    def test_guest_page_loads_correctly(self):
        """Kiểm tra xem hàm guestPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('guestPage'))
        self.assertEqual(response.status_code, 200)

    def test_guest_page_uses_correct_template(self):
        """Kiểm tra xem hàm guestPage có sử dụng đúng template không"""
        response = self.client.get(reverse('guestPage'))
        self.assertTemplateUsed(response, '1_1_guestHome_page.html')


class AboutUsPageViewTests(TestCase):
    """
    Kiểm thử cho hàm aboutUsPage
    """

    def test_about_us_page_loads_correctly(self):
        """Kiểm tra xem hàm aboutUsPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('aboutUsPage'))
        self.assertEqual(response.status_code, 200)

    def test_about_us_page_uses_correct_template(self):
        """Kiểm tra xem hàm aboutUsPage có sử dụng đúng template không"""
        response = self.client.get(reverse('aboutUsPage'))
        self.assertTemplateUsed(response, '1_2_aboutUs_page.html')


class PrivacyPolicyPageViewTests(TestCase):
    """
    Kiểm thử cho hàm privacyPolicyPage
    """

    def test_privacy_policy_page_loads_correctly(self):
        """Kiểm tra xem hàm privacyPolicyPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('privacyPolicyPage'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy_page_uses_correct_template(self):
        """Kiểm tra xem hàm privacyPolicyPage có sử dụng đúng template không"""
        response = self.client.get(reverse('privacyPolicyPage'))
        self.assertTemplateUsed(response, '1_3_privacyPolicy_page.html')


class PreferencesPageViewTests(TestCase):
    """
    Kiểm thử cho hàm preferencesPage
    """

    def test_preferences_page_loads_correctly(self):
        """Kiểm tra xem hàm preferencesPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('preferencesPage'))
        self.assertEqual(response.status_code, 200)

    def test_preferences_page_uses_correct_template(self):
        """Kiểm tra xem hàm preferencesPage có sử dụng đúng template không"""
        response = self.client.get(reverse('preferencesPage'))
        self.assertTemplateUsed(response, '4_3_preferences_page.html')


class SimulationPageViewTests(TestCase):
    """
    Kiểm thử cho hàm SimulationPage
    """

    def test_simulation_page_loads_correctly(self):
        """Kiểm tra xem hàm SimulationPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('simulationPage'))
        self.assertEqual(response.status_code, 200)

    def test_simulation_page_uses_correct_template(self):
        """Kiểm tra xem hàm SimulationPage có sử dụng đúng template không"""
        response = self.client.get(reverse('simulationPage'))
        self.assertTemplateUsed(response, '15_simulation_page.html')


class ResetPasswordPageViewTests(TestCase):
    """
    Kiểm thử cho hàm resetPasswordPage
    """

    def test_reset_password_page_loads_correctly(self):
        """Kiểm tra xem hàm resetPasswordPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('resetPasswordPage', args=['test@example.com']))
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page_uses_correct_template(self):
        """Kiểm tra xem hàm resetPasswordPage có sử dụng đúng template không"""
        response = self.client.get(reverse('resetPasswordPage', args=['test@example.com']))
        self.assertTemplateUsed(response, '5_4_reset_password_page.html')


class AccountSettingsPageViewTests(TestCase):
    """
    Kiểm thử cho hàm AccountSettingsPage
    """

    def test_account_settings_page_loads_correctly(self):
        """Kiểm tra xem hàm AccountSettingsPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('accountSettingsPage'))
        self.assertEqual(response.status_code, 200)

    def test_account_settings_page_uses_correct_template(self):
        """Kiểm tra xem hàm AccountSettingsPage có sử dụng đúng template không"""
        response = self.client.get(reverse('accountSettingsPage'))
        self.assertTemplateUsed(response, '11_accountSettings_page.html')


class ViewBookPageViewTests(TestCase):
    """
    Kiểm thử cho hàm ViewBookPage
    """

    def test_view_book_page_loads_correctly(self):
        """Kiểm tra xem hàm ViewBookPage có trả về mã trạng thái 200 không"""
        # Sử dụng ID sách là 1 cho mục đích kiểm thử
        response = self.client.get(reverse('ViewBookPage', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_view_book_page_uses_correct_template(self):
        """Kiểm tra xem hàm ViewBookPage có sử dụng đúng template không"""
        # Sử dụng ID sách là 1 cho mục đích kiểm thử
        response = self.client.get(reverse('ViewBookPage', args=[1]))
        self.assertTemplateUsed(response, '12_viewBook_page.html')


class OpenBookPageViewTests(TestCase):
    """
    Kiểm thử cho hàm OpenBookPage
    """

    def setUp(self):
        """Thiết lập dữ liệu cần thiết cho kiểm thử"""
        # Tạo một category để liên kết với book
        self.category = Category.objects.create(
            category_name="Test Category"
        )

        # Tạo một Book giả để kiểm thử với đầy đủ các trường cần thiết
        self.book = Book.objects.create(
            book_name="Test Book",
            book_author="Test Author",
            book_type="Test Type",
            book_description="Test Description",
            book_reading_counter=0,
            book_rating_avg=0,
            book_favourite_counter=0,
            status="Accepted",  # Thêm trường status
            category=self.category  # Liên kết với category
        )

    def test_open_book_page_loads_correctly(self):
        """Kiểm tra xem hàm OpenBookPage có trả về mã trạng thái 200 không"""
        response = self.client.get(reverse('OpenBookPage', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 200)

    def test_open_book_page_uses_correct_template(self):
        """Kiểm tra xem hàm OpenBookPage có sử dụng đúng template không"""
        response = self.client.get(reverse('OpenBookPage', args=[self.book.book_id]))
        self.assertTemplateUsed(response, '14_openBook_page.html')


class CategoryListViewTests(APITestCase):
    """
    Kiểm thử cho hàm CategoryListView
    """

    def setUp(self):
        """Thiết lập dữ liệu cần thiết cho kiểm thử"""
        # Tạo một số category giả lập cho việc kiểm thử
        self.category1 = Category.objects.create(category_name="Fiction")
        self.category2 = Category.objects.create(category_name="Science")
        self.category3 = Category.objects.create(category_name="History")

    def test_category_list_view_returns_200(self):
        """Kiểm tra xem CategoryListView có trả về mã trạng thái 200 không"""
        response = self.client.get('/getAllCategories/')
        self.assertEqual(response.status_code, 200)

    def test_category_list_view_returns_all_categories(self):
        """Kiểm tra xem CategoryListView có trả về đúng tất cả danh sách category không"""
        response = self.client.get('/getAllCategories/')
        self.assertEqual(len(response.data), 3)
        # Kiểm tra nội dung trả về
        category_names = [item['category_name'] for item in response.data]
        self.assertIn("Fiction", category_names)
        self.assertIn("Science", category_names)
        self.assertIn("History", category_names)


class UserPreferencesViewTests(APITestCase):
    """
    Kiểm thử cho hàm UserPreferencesView
    """

    def setUp(self):
        """Thiết lập dữ liệu cần thiết cho kiểm thử"""
        # Tạo user và reader
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password="password",
            is_active=True
        )
        self.reader = Reader.objects.create(user=self.user)

        # Tạo user khác không có reader
        self.user_without_reader = User.objects.create(
            user_name="noreaderyetuser",
            email="noreader@example.com",
            user_password="password",
            is_active=True
        )

        # Tạo user với reader nhưng không có preferences
        self.user_no_preferences = User.objects.create(
            user_name="nopreferences",
            email="nopreferences@example.com",
            user_password="password",
            is_active=True
        )
        self.reader_no_preferences = Reader.objects.create(user=self.user_no_preferences)

        # Tạo category
        self.category = Category.objects.create(category_name="Fiction")

        # Tạo preferences
        self.preference = Preferences.objects.create(
            reader=self.reader,
            category=self.category
        )

    def test_user_preferences_view_returns_200(self):
        """Kiểm tra xem UserPreferencesView có trả về mã trạng thái 200 không"""
        response = self.client.get(f'/user_preferences/{self.user.user_id}/')
        self.assertEqual(response.status_code, 200)

    def test_user_preferences_view_returns_correct_preferences(self):
        """Kiểm tra xem UserPreferencesView có trả về đúng preferences của user không"""
        response = self.client.get(f'/user_preferences/{self.user.user_id}/')
        self.assertIn('preferences', response.data)
        self.assertEqual(len(response.data['preferences']), 1)
        self.assertEqual(response.data['preferences'][0]['category_id'], self.category.category_id)

    def test_user_preferences_view_returns_404_if_reader_not_found(self):
        """Kiểm tra xem UserPreferencesView có trả về lỗi 404 khi không tìm thấy reader không"""
        response = self.client.get(f'/user_preferences/{self.user_without_reader.user_id}/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'User not found')

    def test_user_preferences_view_returns_empty_preferences_list(self):
        """Kiểm tra xem UserPreferencesView có trả về danh sách preferences rỗng khi user không có preferences không"""
        response = self.client.get(f'/user_preferences/{self.user_no_preferences.user_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('preferences', response.data)
        self.assertEqual(len(response.data['preferences']), 0)


class SummarizeTextTests(TestCase):
    """
    Kiểm thử cho hàm summarize_text
    """

    def test_summarize_text_returns_content(self):
        """Kiểm tra xem summarize_text có trả về nội dung không rỗng"""
        from .views import summarize_text
        from django.test.client import RequestFactory
        import json

        # Sử dụng RequestFactory để tạo request giả lập
        factory = RequestFactory()
        text = """Đây là một đoạn văn bản dài. Nội dung này cần được tóm tắt.
                Đây là một đoạn văn bản dài. Nội dung này cần được tóm tắt.
                Đây là một đoạn văn bản dài. Nội dung này cần được tóm tắt."""

        # Tạo request với body là JSON
        request = factory.post(
            '/',
            data=json.dumps({'text': text}),
            content_type='application/json'
        )
        response = summarize_text(request)

        # Kiểm tra status code và parse JSON response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('result', response_data)
        self.assertTrue(len(response_data['result']) > 0)

    def test_summarize_text_handles_empty_input(self):
        """Kiểm tra xem summarize_text xử lý đúng khi không có dữ liệu đầu vào"""
        from .views import summarize_text
        from django.test.client import RequestFactory
        import json

        # Sử dụng RequestFactory để tạo request giả lập
        factory = RequestFactory()

        # Tạo request với body là JSON và text rỗng
        request = factory.post(
            '/',
            data=json.dumps({'text': ""}),
            content_type='application/json'
        )
        response = summarize_text(request)

        self.assertEqual(response.status_code, 400)


class SavePreferencesTests(TestCase):
    """
    Kiểm thử cho hàm save_preferences
    """

    def setUp(self):
        """Thiết lập dữ liệu cần thiết cho kiểm thử"""
        # Tạo user và reader
        self.user = User.objects.create(
            user_name="testuser",
            email="test@example.com",
            user_password="password",
            is_active=True
        )
        self.reader = Reader.objects.create(user=self.user)

        # Tạo các category
        self.category1 = Category.objects.create(category_name="Fiction")
        self.category2 = Category.objects.create(category_name="Science")

    def test_save_preferences_success(self):
        """Kiểm tra xem save_preferences hoạt động đúng khi dữ liệu hợp lệ"""
        from django.test.client import RequestFactory
        from .views import save_preferences

        factory = RequestFactory()
        request = factory.post('/', {
            'user_id': self.user.user_id,
            'preferences': f"{self.category1.category_id},{self.category2.category_id}"
        })

        response = save_preferences(request)

        self.assertEqual(response.status_code, 200)

        # Kiểm tra xem preferences đã được lưu chưa
        preferences = Preferences.objects.filter(reader=self.reader)
        self.assertEqual(preferences.count(), 2)
        category_ids = [pref.category_id for pref in preferences]
        self.assertIn(self.category1.category_id, category_ids)
        self.assertIn(self.category2.category_id, category_ids)
    def test_save_preferences_missing_data(self):
        """Kiểm tra xem save_preferences xử lý lỗi khi thiếu dữ liệu"""
        from django.test.client import RequestFactory
        from .views import save_preferences

        factory = RequestFactory()

        # Thiếu user_id
        request = factory.post('/', {
            'preferences': f"{self.category1.category_id}"
        })

        response = save_preferences(request)

        self.assertEqual(response.status_code, 400)

    def test_save_preferences_user_not_found(self):
        """Kiểm tra xem save_preferences xử lý lỗi khi không tìm thấy reader"""
        from django.test.client import RequestFactory
        from .views import save_preferences

        factory = RequestFactory()

        # Sử dụng user_id không tồn tại
        non_existent_user_id = 9999
        request = factory.post('/', {
            'user_id': non_existent_user_id,
            'preferences': f"{self.category1.category_id}"
        })

        response = save_preferences(request)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.content.decode())
        self.assertIn('User not found', response.content.decode())

    def test_save_preferences_wrong_method(self):
        """Kiểm tra xem save_preferences xử lý lỗi khi phương thức không phải POST"""
        from django.test.client import RequestFactory
        from .views import save_preferences

        factory = RequestFactory()

        # Sử dụng phương thức GET thay vì POST
        request = factory.get('/')

        response = save_preferences(request)

        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.content.decode())
        self.assertIn('Invalid request method', response.content.decode())
