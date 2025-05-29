from django.shortcuts import redirect, render

# pip install djangorestframework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import *
from .serializers import *

# pip install djangorestframework-jwt
import jwt
import datetime

# pip install django-bcrypt
import bcrypt

#--------
# pip install urlsafe-base64-py
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
#---------
from .pagination import *
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Case, When, Value
from django.db.utils import IntegrityError

#----------
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.contrib import messages

# notes:- guest page_contactUs, regiseration process, book_favourite_counter manual !!!, insert book, copy url confirm register page

#-- redirect page --

def guestPage(request):
    return render(request, '1_1_guestHome_page.html')

def aboutUsPage(request):
    return render(request, '1_2_aboutUs_page.html')

def privacyPolicyPage(request):
    return render(request, '1_3_privacyPolicy_page.html')

def loginPage(request):
    return render(request, '2_login_page.html')

def registerPage(request):
    return render(request, '3_register_page.html')

def confirm_email_register(request):
    email = request.GET.get('email', '')  # Retrieve email from query parameters
    return render(request, '4_1_confirm_email_register_page.html', {'email': email})

def preferencesPage(request):
    categories = Category.objects.all()
    return render(request, '4_3_preferences_page.html', {'Category': categories})

def SimulationPage(request):
    return render(request, '15_simulation_page.html')

def findAccountPage(request):
    return render(request, '5_1_find_account_forgetPass_page.html')

def confirm_email_change_password(request):
    email = request.GET.get('email', '')  # Retrieve email from query parameters
    return render(request, '5_2_confirm_email_forgetPass_page.html', {'email': email})

def resetPasswordPage(request, email):
    return render(request, '5_4_reset_password_page.html', {'email': email})

def homePage(request):
    return render(request, '6_home_page.html')

def RankPage(request):
    return render(request, '7_gamefication_page.html')

def WishListPage(request):
    return render(request, '8_wishlist_page.html')

def NotificationPage(request):
    return render(request, '9_notification_page.html')

def MyUploadedBookPage(request):
    return render(request, '10_myUploadedBook_page.html')

def AccountSettingsPage(request):
    categories = Category.objects.all()
    return render(request, '11_accountSettings_page.html', {'Category': categories})

def ViewBookPage(request, book_id):
    return render(request, '12_viewBook_page.html', {'book_id': book_id})

def OpenBookPage(request, book_id):
    book=Book.objects.get(book_id=book_id)
    book.book_reading_counter+=1
    book.save(update_fields=['book_reading_counter'])

    return render(request, '14_openBook_page.html', {'book_id': book_id})

def GuestSearchPage(request):
    search = request.GET.get('search', '')  # Retrieve search from query parameters
    return render(request, '1_4_guestSearch_page.html', {'search': search})

def ReaderSearchPage(request):
    search = request.GET.get('search', '')  # Retrieve search from query parameters
    return render(request, '13_readerSearch_page.html', {'search': search})
#--------------------------------------------------------------------------------------------


#-- login --

class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_password = request.data.get('user_password')


        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Verify the password using bcrypt
            if not bcrypt.checkpw(user_password.encode('utf-8'), user.user_password.encode('utf-8')):
                raise AuthenticationFailed("Incorrect password!", status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    payload = {
                        'id': user.user_id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180), # 3 hours
                        'iat': datetime.datetime.utcnow()
                    }

                    token = jwt.encode(payload, 'secret', algorithm='HS256')

                    # Get current date without time
                    current_date = now()
                    last_login_date = user.last_login if user.last_login else None

                    isDailyLogin = False

                    # Find the Reader entry for this user
                    reader = Reader.objects.get(user_id=user.user_id)

                    if (current_date != last_login_date) or (reader.is_first_time==True):
                        isDailyLogin = True

                        # Update reader points
                        reader.reader_point += 10
                        if(reader.reader_point>=500 and reader.reader_point<1500):
                            reader.reader_rank="Bronze"
                        elif(reader.reader_point>=1500 and reader.reader_point<3000):
                            reader.reader_rank="Silver"
                        elif(reader.reader_point>=3000):
                            reader.reader_rank="Gold"

                        reader.save()


                        # Insert new gamification record
                        Gamification_Record.objects.create(
                            reader_id=reader.reader_id,
                            gamification_description="Daily login",
                            achieved_point=10
                        )

                        Notification.objects.create(
                            reader_id=reader.reader_id,
                            manager_id=2,
                            notification_record="+10 Point for Daily login",
                            notification_title="New Point Achievement"
                        )


                    #Update last_login timestamp
                    user.last_login = now()
                    user.save(update_fields=['last_login'])  # Ensure last_login is updated
                    user.refresh_from_db()

                    return Response({'jwt': token, 'isDailyLogin': isDailyLogin}, status=status.HTTP_200_OK)
                else:
                    raise AuthenticationFailed("Your account has not activated yet.", status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            print(User.objects.all())
            raise AuthenticationFailed("User not found or incorrect password!", status=status.HTTP_401_UNAUTHORIZED)



class RefreshTokenView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            raise AuthenticationFailed("Token is required!", status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'], options={"verify_exp": False})
            user = User.objects.get(user_id=payload['id'])

            if not user.is_active:
                raise AuthenticationFailed("Your account is not active.", status=status.HTTP_401_UNAUTHORIZED)

            # Generate new token
            new_payload = {
                'id': user.user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180),  # 3 hours
                'iat': datetime.datetime.utcnow()
            }
            new_token = jwt.encode(new_payload, 'secret', algorithm='HS256')

            return Response({'jwt': new_token}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired!", status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token!", status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found!", status=status.HTTP_401_UNAUTHORIZED)

#--------------------------------------------------------------------------------------------


#-- register--


class RegisterAPIView(APIView):
    def post(self, request):

        try:
            user_name = request.data.get('user_name')
            email = request.data.get('email')
            user_password = request.data.get('user_password')

            # Hash the password using bcrypt and verify hashing
            # hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Ensure it's stored as a string


            # Save the user with the hashed password
            user = User(user_name=user_name, email=email, user_password=hashed_password)
            user.save()

            reader=Reader(user=user)
            reader.save()

            send_verification_email_register(user=user,request=request)

            return Response(
                {
                'message': 'User registered successfully. Please check your email to verify your account.',
                'email': email
                }, status=status.HTTP_200_OK)

        except IntegrityError as e:
            if 'unique constraint' in str(e):
                return Response({'error': 'This email address is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#--------------------------------------------------------------------------------------------


#-- register confirmation process --


class ExpiringTokenGenerator_register(PasswordResetTokenGenerator):
    def make_token(self, user):
        """
        Override the default method to include an expiration time (30 minute).
        """
        timestamp = str(int(timezone.now().timestamp()))  # Current timestamp
        expiration_time = (timezone.now() + datetime.timedelta(minutes=30)).timestamp()  # Token expires in 30 minute
        return f"{super().make_token(user)}-{int(expiration_time)}"  # Append expiration time to token

    def check_token(self, user, token):
        """
        Override the default method to check if the token has expired.
        """
        try:
            base_token, expiration_time = token.rsplit('-', 1)
            expiration_time = float(expiration_time)
            if timezone.now().timestamp() > expiration_time:
                return False  # Token is expired
            return super().check_token(user, base_token)
        except (ValueError, IndexError):
            return False  # Invalid token format

token_generator_register = ExpiringTokenGenerator_register()

# send email for register
def send_verification_email_register(user, request):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator_register.make_token(user)  # Use the custom token generator

    mail_subject = 'Activate your account.'
    message = render_to_string('4_2_email_templet_register.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': uid,
        'token': token,
        'user_name': user.user_name,
    })

    email_message = EmailMultiAlternatives(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email_message.attach_alternative(message, "text/html")
    email_message.send()


def send_another_email(request, email):
    try:
        user = User.objects.get(email=email)
        send_verification_email_register(user, request)
        return JsonResponse({'message': 'Verification email sent successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User with the provided email does not exist.'}, status=404)


class activate_register(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode user ID from the token
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and not expired
        if token_generator_register.check_token(user, token) and not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated successfully.')
            return redirect('loginPage')  # This should return a redirect response
        elif user.is_active:
            messages.info(request, 'Your account is already activated.')
            return redirect('loginPage')  # This should return a redirect response
        else: ####################### change
            messages.error(request, 'Activation link is invalid or expired.')
            return redirect('loginPage')  # This should return a redirect response
#--------------------------------------------------------------------------------------------


#-- forget password process --


class EmailExistView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)
            return Response({"exists": True, "message": "Email is found."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"exists": False, "message": "Email not found."}, status=status.HTTP_404_NOT_FOUND)


class ExpiringTokenGenerator_forget_pass(PasswordResetTokenGenerator):
    def make_token(self, user):
        """
        Override the default method to include an expiration time (30 minute).
        """
        timestamp = str(int(timezone.now().timestamp()))  # Current timestamp
        expiration_time = (timezone.now() + datetime.timedelta(minutes=30)).timestamp()  # Token expires in 30 minute
        return f"{super().make_token(user)}-{int(expiration_time)}"  # Append expiration time to token

    def check_token(self, user, token):
        """
        Override the default method to check if the token has expired.
        """
        try:
            base_token, expiration_time = token.rsplit('-', 1)
            expiration_time = float(expiration_time)
            if timezone.now().timestamp() > expiration_time:
                return False  # Token is expired
            return super().check_token(user, base_token)
        except (ValueError, IndexError):
            return False  # Invalid token format

token_generator_forget_pass = ExpiringTokenGenerator_forget_pass()

# send email for change password
def send_verification_email_forget_pass(user, request):

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator_forget_pass.make_token(user)  # Use the custom token generator

    mail_subject = 'Change Account Password.'
    message = render_to_string('5_3_email_templet_forgetPass.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': uid,
        'token': token,
        'user_name': user.user_name,
    })

    email_message = EmailMultiAlternatives(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email_message.attach_alternative(message, "text/html")
    email_message.send()


def send_another_email_change_pass(request, email):
    try:
        user = User.objects.get(email=email)
        send_verification_email_forget_pass(user, request)
        return JsonResponse({'message': 'Verification email sent successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User with the provided email does not exist.'}, status=404)

class activate_change_password(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode user ID from the token
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            email = user.email
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid and not expired
        if token_generator_forget_pass.check_token(user, token):
            return redirect('resetPasswordPage',email)  # This should return a redirect response
        else: ####################### change
            messages.error(request, 'Activation link is invalid or expired.')
            return redirect('loginPage')  # This should return a redirect response

class reset_password(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_password=request.data.get('user_password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Hash the password using bcrypt and verify hashing
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            user.user_password = hashed_password
            user.save()
            messages.success(request, 'Your account has reset password successfully.')
            return redirect('loginPage')
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserChangePasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        curr_password = request.data.get('curr_password')
        new_password = request.data.get('new_password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Verify the current password using bcrypt
            if not bcrypt.checkpw(curr_password.encode('utf-8'), user.user_password.encode('utf-8')):
                return Response({"error": "Incorrect Current password!"}, status=status.HTTP_401_UNAUTHORIZED)

            # Hash the password using bcrypt and verify hashing
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            user.user_password = hashed_password
            user.save()

            return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            raise AuthenticationFailed("User not found!", status=status.HTTP_404_NOT_FOUND)


class UpdateReaderIsFirstTime(APIView):
    def post(self, request):
        try:
            user_id = request.data.get("user_id")

            reader = Reader.objects.filter(user_id=user_id).first()
            if reader:
                reader.is_first_time = False
                reader.save()
                return JsonResponse({"message": "Updated successfully"}, status=200)
            else:
                return JsonResponse({"error": "Reader not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

def save_preferences(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        category_ids = request.POST.get("preferences")  # Multiple categories

        if not user_id or not category_ids:
            return JsonResponse({'error': 'User ID or categories not provided'}, status=400)

        category_ids = category_ids.split(',')  # Convert string to list

        reader = Reader.objects.filter(user_id=user_id).first()
        if not reader:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Save multiple selected categories
        Preferences.objects.filter(reader_id=reader.reader_id).delete()  # Clear old preferences
        Preferences.objects.bulk_create([
            Preferences(reader_id=reader.reader_id, category_id=cat_id) for cat_id in category_ids
        ])

        return JsonResponse({'message': 'Preferences saved successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
#--------------------------------------------------------------------------------------------


#-- list category
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#-- list category by user id
class UserPreferencesView(APIView):
    def get(self, request, user_id):
        reader = Reader.objects.filter(user_id=user_id).first()
        if not reader:
            return Response({'error': 'User not found'}, status=404)

        preferences = Preferences.objects.filter(reader_id=reader.reader_id).select_related('category')

        data = [
            {"category_id": pref.category.category_id}  # Use the correct field
            for pref in preferences
        ]

        return Response({"preferences": data})

#--------------------------------------------------------------------------------------------

#-- get name from id
class UserNameListView(APIView):
    def get(self, request, user_id):
        try:
            # Fetch the user by ID
            user = User.objects.get(user_id=user_id)
            # Return the user_name
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#--------------------------------------------------------------------------------------------

#-- get reader
class ReaderInfoListView(APIView):
    def get(self, request):

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
            serializer = ReaderSerializer(reader)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

#--------------------------------------------------------------------------------------------

#-- get book
class BookInfoListView(APIView):
    def get(self, request):

        book_id = request.query_params.get('book_id')

        try:
            book = Book.objects.get(book_id=book_id)
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reader.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_400_BAD_REQUEST)


class ContinueReadingView(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        reader_id = request.data.get("reader_id")

        bookContinueReading=BookContinueReading.objects.filter(book_id=book_id, reader_id=reader_id).first()

        if bookContinueReading is None:
            BookContinueReading.objects.create(
                book_id=book_id,
                reader_id=reader_id
            )

        return JsonResponse({"message": "Continue reading created"})

class UploadedByView(APIView):
    def get(self, request):

        book_id = request.query_params.get('book_id')

        uploadedBook=UploadedBook.objects.filter(book_id=book_id).first()

        if uploadedBook == None:
            return Response("Manager", status=status.HTTP_200_OK)
        else:
            reader = Reader.objects.get(reader_id=uploadedBook.reader_id)
            user = User.objects.get(user_id=reader.user_id)
            return Response(user.user_name, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------

#-- list book (pagination achived)
class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- list most readed book (pagination achived)
class MostReaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.filter(status=Book.Status.ACCEPTED).order_by('-book_reading_counter')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- list last uploaded book (pagination achived)
class LastUploaded_BookListView(APIView):
    def get(self, request):
        books = Book.objects.filter(status=Book.Status.ACCEPTED).order_by('-book_uploaded_date')
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- add rating and review
class AddRatingAndReviewView(APIView):
    def post(self, request):
        # Extract data from request
        book_id = request.data.get("book_id")
        user_id = request.data.get("user_id")
        rating = request.data.get("rating")
        review = request.data.get("review")

        # Validate that required fields are present
        if not (book_id and user_id and rating is not None and review):
            return Response({"error": "All fields (book_id, user_id, rating, review) are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate rating range
        if not (1 <= rating <= 5):
            return Response({"error": "Rating must be between 1 and 5."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Fetch the book and reader objects
        try:
            book = Book.objects.get(pk=book_id)
            reader = Reader.objects.get(user_id=user_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if book is accepted
        if book.status != Book.Status.ACCEPTED:
            return Response({"error": "Cannot review a book that is not accepted."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate review
        if Rating_And_Review.objects.filter(book=book, reader=reader).exists():
            return Response({"error": "You have already reviewed this book."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the Rating_And_Review entry
        Rating_And_Review.objects.create(
            book=book,
            reader=reader,
            rating=rating,
            review=review
        )

        # Recalculate the average rating for the book
        ratings = Rating_And_Review.objects.filter(book=book).values_list('rating', flat=True)
        total_ratings = sum(ratings)
        rating_count = len(ratings)
        average_rating = round(total_ratings / rating_count) if rating_count > 0 else 0

        # Update the book's average rating
        book.book_rating_avg = average_rating
        book.save()

        # Update reader points
        reader.reader_point += 20
        if(reader.reader_point>=500 and reader.reader_point<1500):
            reader.reader_rank="Bronze"
        elif(reader.reader_point>=1500 and reader.reader_point<3000):
            reader.reader_rank="Silver"
        elif(reader.reader_point>=3000):
            reader.reader_rank="Gold"

        reader.save()

        # Insert new gamification record
        Gamification_Record.objects.create(
            reader_id=reader.reader_id,
            gamification_description="Rating And Review Book Achievement",
            achieved_point=20
        )

        Notification.objects.create(
            reader_id=reader.reader_id,
            manager_id=2,
            notification_record="+20 Point for Rating And Review Book",
            notification_title="New Point Achievement"
        )

        return Response({"message": "Rating and review added successfully."}, status=status.HTTP_201_CREATED)

#--------------------------------------------------------------------------------------------
#-- list rating and review:

class RatingAndReviewListView(APIView):
    def get(self, request):
        book_id = request.query_params.get("book_id")

        try:
            # Retrieve all rating and reviews, order by 'id' in descending order
            rating_review = Rating_And_Review.objects.filter(book_id=book_id).select_related('reader__user').order_by('-rating_and_review_id')

            # Prepare the data with user_name added
            reviews_data = []
            for review in rating_review:
                review_data = {
                    **RatingAndReviewSerializer(review).data,  # Serialize the review
                    'user_name': review.reader.user.user_name  # Add the user's name from related Reader and User
                }
                reviews_data.append(review_data)

            paginator = RatingAndReviewPagination()
            result_page = paginator.paginate_queryset(reviews_data, request)
            return paginator.get_paginated_response(result_page)

        except Rating_And_Review.DoesNotExist:
            return Response({"error": "rating and review not found"}, status=status.HTTP_400_BAD_REQUEST)




#--------------------------------------------------------------------------------------------

#-- list Most Rating book (pagination achived)


class MostRating_BookListView(APIView):
    def get(self, request):
        # Get the filter parameters from the request query
        rating_filter = request.query_params.get('rating', None)
        reading_counter_filter = request.query_params.get('reading_counter', None)

        # Filter books by status
        books = Book.objects.filter(status=Book.Status.ACCEPTED)

        # Apply rating filter if provided
        if rating_filter:
            try:
                rating_filter = int(rating_filter)
                books = books.filter(book_rating_avg__gte=rating_filter)  # Books with rating greater than or equal to provided value
            except ValueError:
                return Response({"error": "Invalid rating filter value"}, status=status.HTTP_400_BAD_REQUEST)

        # Apply reading_counter filter if provided
        if reading_counter_filter:
            try:
                reading_counter_filter = int(reading_counter_filter)
                books = books.filter(book_reading_counter__gte=reading_counter_filter)  # Books with reading_counter greater than or equal to provided value
            except ValueError:
                return Response({"error": "Invalid reading_counter filter value"}, status=status.HTTP_400_BAD_REQUEST)

        # Order by book_rating_avg and book_reading_counter
        books = books.order_by('-book_rating_avg', '-book_reading_counter')  # First by rating, then by reading counter

        # Pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


#--------------------------------------------------------------------------------------------

#-- list searched book
class BookSearchView(APIView):
    def get(self, request):
        # Get parameters from the request
        search_query = request.query_params.get('search', '').strip()
        sort_by = request.query_params.get('sort_by', '')
        category_ids = request.query_params.get('category', None)
        min_rating = request.query_params.get('min_rating', None)

        # Base queryset, only filter if search query is provided
        books = Book.objects.filter(status=Book.Status.ACCEPTED)
        if search_query:
            books = books.filter(book_name__icontains=search_query)

        # Filter by multiple categories if provided
        if category_ids:
            category_id_list = category_ids.split(',')
            books = books.filter(category__category_id__in=category_id_list)

        # Filter by minimum rating if provided
        if min_rating:
            books = books.filter(book_rating_avg__gte=min_rating).order_by('book_rating_avg')

        # Apply sorting
        if sort_by == 'reviewed':
            books = books.order_by('-book_reading_counter')
        elif sort_by == 'favourite':
            books = books.order_by('-book_favourite_counter')
        elif sort_by == 'newest':
            books = books.order_by('-book_uploaded_date')

        # Apply pagination
        paginator = BookSearchPagination()
        paginated_books = paginator.paginate_queryset(books, request)

        # Serialize the paginated data
        serializer = BookSerializer(paginated_books, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)



def add_book(request):
    if request.method == 'POST':
        try:
            # Retrieve POST data
            book_name = request.POST.get('title')
            book_author = request.POST.get('author')
            book_barcode = request.POST.get('barcode')
            book_description = request.POST.get('description')
            category_id = request.POST.get('category')
            book_file = request.FILES.get('bookfile')
            book_image = request.FILES.get('bookImage')
            reader_id=request.POST.get('reader_id')

            # Validate category
            category = Category.objects.filter(category_id=category_id).first()
            if not category:
                return JsonResponse({'status': 'error', 'message': 'Invalid category.'}, status=400)

            # Save the book without file and image to get the book ID
            book = Book.objects.create(
                book_name=book_name,
                book_author=book_author,
                book_type=category.category_name,
                book_barcode=book_barcode,
                book_description=book_description,
                category_id=category_id,
                book_reading_counter=0,
                book_rating_avg=0,
                book_favourite_counter=0,
                status=Book.Status.PENDING,
                book_uploaded_date=now()
            )

            # Rename and save the book file
            book_file_extension = book_file.name.split('.')[-1]
            book_file_name = f"{book.book_id}_file.{book_file_extension}"
            book.book_file.save(book_file_name, book_file)

            if book_image is not None:
                book_image_extension = book_image.name.split('.')[-1]
                book_image_name = f"{book.book_id}_image.{book_image_extension}"
                book.book_image.save(book_image_name, book_image)


            # Save the book instance with updated file paths
            book.save()

            reader = Reader.objects.filter(reader_id=reader_id).first()
            # Update reader points
            reader.reader_point += 50
            if(reader.reader_point>=500 and reader.reader_point<1500):
                reader.reader_rank="Bronze"
            elif(reader.reader_point>=1500 and reader.reader_point<3000):
                reader.reader_rank="Silver"
            elif(reader.reader_point>=3000):
                reader.reader_rank="Gold"

            reader.save()
            UploadedBook.objects.create(
                reader_id=reader_id,
                book_id=book.book_id
            )

            # Insert new gamification record
            Gamification_Record.objects.create(
                reader_id=reader_id,
                gamification_description="Upload Books Achievement",
                achieved_point=50
            )

            Notification.objects.create(
                reader_id=reader_id,
                manager_id=2,
                notification_record="+50 Point for Uploaded Books Achievement",
                notification_title="New Point Achievement"
            )


            return JsonResponse({'status': 'success', 'message': 'Book added successfully!', 'book_id': book.book_id})

        except Exception as e:
            # Log the exception
            print("Error occurred:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
#-----------------------------------Reader

class MostReadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id directly from the query parameters
        user_id = request.query_params.get('user_id')

        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)

        # Filter books based on the user's preferred categories
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_reading_counter')
        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

class MostRatingPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)

        # Filter books based on the user's preferred categories and order by rating
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_rating_avg')

        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

class LastUploadedPreferences_BookListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get categories from user preferences based on user_id
        user_preferences = Preferences.objects.filter(reader__user__user_id=user_id).values_list('category', flat=True)

        # Filter books based on the user's preferred categories and order by upload date
        books = Book.objects.filter(category__in=user_preferences, status=Book.Status.ACCEPTED).order_by('-book_uploaded_date')

        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- list continue reading book (pagination achived)
class BookContinueReadingListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter books in the BookContinueReading table for the specified user and order in reverse
        continue_reading_books = Book.objects.filter(bookcontinuereading__reader__user__user_id=user_id, status=Book.Status.ACCEPTED).order_by('-bookcontinuereading__continue_reading_id')

        # Apply pagination
        paginator = BookPagination()
        result_page = paginator.paginate_queryset(continue_reading_books, request)
        serializer = BookSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

class LastThreeWishListView(APIView):
    def get(self, request):

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the last three wishlist items for the given reader, ordered by `wish_list_id`
        last_three_items = WishList.objects.filter(reader_id=reader.reader_id).order_by('-wish_list_id')[:3]

        # Extract the book_ids from the last three wishlist items, preserving the order
        book_ids = [item.book_id for item in last_three_items]

        # Fetch the corresponding Book objects using the extracted book_ids in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )

        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------------------------

class LastThreeNotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters

        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)


        # Get the last three notifications for the given reader, ordered by `notification_id`
        last_three_items = Notification.objects.filter(reader_id=reader.reader_id).order_by('-notification_id')[:3]

        # Serialize the Book objects
        serializer = NotificationListSerializer(last_three_items, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------------------------

#-- list wishlist (pagination achived)
class WishListListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = WishList.objects.filter(reader_id=reader.reader_id).order_by('-wish_list_id')

        # Paginate the results
        paginator = WishListPagination()
        result_page = paginator.paginate_queryset(items, request)

        # Extract the book_ids from the wishlist items
        book_ids = [item.book_id for item in result_page]

        # Fetch the corresponding Book objects in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )

        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

class AddBookToWishlist(APIView):
    def post(self, request):
        # Retrieve book_id and user_id from the request body
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')

        # Validate book_id and user_id
        if not book_id or not user_id:
            return Response({"error": "Book ID and User ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the book existence
        try:
            book = Book.objects.get(book_id=book_id)
            
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the book is already in the wishlist
        if WishList.objects.filter(book=book, reader=reader).exists():
            return Response({"error": "Book already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)

        # Add the book to the wishlist
        WishList.objects.create(book=book, reader=reader)

        # Increment the book's favorite counter
        book.book_favourite_counter = (book.book_favourite_counter or 0) + 1
        book.save(update_fields=['book_favourite_counter'])

        return Response(
            {"message": "Book added to wishlist", "book_favourite_counter": book.book_favourite_counter},
            status=status.HTTP_201_CREATED
        )



#--------------------------------------------------------------------------------------------

class RemoveBookFromWishlist(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the book from the wishlist
        try:
            wishlist_item = WishList.objects.get(book_id=book_id, reader_id=reader.reader_id)
            wishlist_item.delete()

            # Optionally, decrement the book's favourite counter here
            book = Book.objects.get(book_id=book_id)
            book.book_favourite_counter -= 1
            book.save()

            return Response({"message": "Book removed from wishlist"}, status=status.HTTP_200_OK)
        except WishList.DoesNotExist:
            return Response({"error": "Book not in wishlist"}, status=status.HTTP_400_BAD_REQUEST)

#--------------------------------------------------------------------------------------------
class CheckBookInWishlist(APIView):
    def get(self, request):
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book is in the wishlist
        if WishList.objects.filter(book_id=book_id, reader_id=reader.reader_id).exists():
            return Response({"in_wishlist": True}, status=status.HTTP_200_OK)
        else:
            return Response({"in_wishlist": False}, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------------------------

#-- list notification (pagination achived)
class NotificationListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the notifications for the given reader
        notifications = Notification.objects.filter(reader_id=reader.reader_id).order_by('-notification_id')

        # Apply pagination
        paginator = NotificationPagination()
        result_page = paginator.paginate_queryset(notifications, request)

        serializer = NotificationListSerializer(result_page, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------

#-- insert feedback
class InsertFeedbackView(APIView):
    def post(self, request):
        # Get the reader_id and feedback description from the request data
        user_id = request.data.get('user_id')
        feedback_description = request.data.get('feedback_description')

        if not user_id or not feedback_description:
            return Response({"error": "User ID and feedback description are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new FeedBack record
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        feedback = FeedBack.objects.create(reader_id=reader.reader_id, feedback_description=feedback_description)

        # Update reader points
        reader.reader_point += 30
        if(reader.reader_point>=500 and reader.reader_point<1500):
            reader.reader_rank="Bronze"
        elif(reader.reader_point>=1500 and reader.reader_point<3000):
            reader.reader_rank="Silver"
        elif(reader.reader_point>=3000):
            reader.reader_rank="Gold"

        reader.save()

        # Insert new gamification record
        Gamification_Record.objects.create(
            reader_id=reader.reader_id,
            gamification_description="Add Feedback for System Achievement",
            achieved_point=30
        )

        Notification.objects.create(
            reader_id=reader.reader_id,
            manager_id=2,
            notification_record="+30 Point for Feedback for System Achievement",
            notification_title="New Point Achievement"
        )

        # Serialize the feedback object
        serializer = FeedBackSerializer(feedback)

        # Return the serialized data as response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#--------------------------------------------------------------------------------------------

#-- list uploaded_book (pagination achived)
class UploadedBookListView(APIView):
    def get(self, request):
        # Get the reader_id from query parameters
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not user_id:
            return Response({"error": "User ID not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the wishlist items for the given reader, ordered by `wish_list_id`
        items = UploadedBook.objects.filter(reader_id=reader.reader_id).order_by('-uploaded_book_id')

        # Paginate the results
        paginator = UploadedBookPagination()
        result_page = paginator.paginate_queryset(items, request)

        # Extract the book_ids from the wishlist items
        book_ids = [item.book_id for item in result_page]

        # Fetch the corresponding Book objects in the same order as book_ids
        books = Book.objects.filter(book_id__in=book_ids).order_by(
            Case(*[When(book_id=book_id, then=pos) for pos, book_id in enumerate(book_ids)], default=0)
        )

        # Serialize the Book objects
        serializer = BookSerializer(books, many=True)

        # Return the paginated response with serialized data
        return paginator.get_paginated_response(serializer.data)

#--------------------------------------------------------------------------------------------
#-- remove uploaded_book (pagination achived)

class RemoveUploadedBookView(APIView):
    def delete(self, request):
        # Get the book_id and user_id from query parameters
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        # Validate book_id and user_id
        if not book_id or not user_id:
            return Response({"error": "Both book_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Try to find the UploadedBook record
        try:
            uploaded_book = UploadedBook.objects.get(book_id=book_id, reader_id=reader.reader_id)
            book=Book.objects.get(book_id=book_id)

        except UploadedBook.DoesNotExist:
            return Response({"error": "UploadedBook record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Delete the record
        uploaded_book.delete()
        book.delete()

        # Return a success response
        return Response({"message": "Book successfully removed from uploaded books"}, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------
#-- list uploaded_book (pagination achived)
class CreateBookView(APIView):
    def post(self, request):
        # Extract the data from the request body
        data = request.data

        # Serialize the data using a serializer
        serializer = BookSerializer(data=data)

        if serializer.is_valid():
            # Save the new book to the database
            serializer.save()
            return Response({"message": "Book created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#--------------------------------------------------------------------------------------------

#-- gamefication record (pagination achived)
class GamificationRecordListView(APIView):
    def get(self, request):
        # Get the user_id from query parameters
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the reader associated with the user
        try:
            reader = Reader.objects.get(user_id=user_id)
        except Reader.DoesNotExist:
            return Response({"error": "Reader not found"}, status=status.HTTP_404_NOT_FOUND)

        # Filter records for the specified user and order by date_and_time (most recent first)
        gamification_records = Gamification_Record.objects.filter(reader_id=reader.reader_id).order_by('-date_and_time')

        # Apply pagination
        paginator = GameficationPagination()
        result_page = paginator.paginate_queryset(gamification_records, request)
        serializer = GameficationSerializer(result_page, many=True)  # Use the correct serializer here

        return paginator.get_paginated_response(serializer.data)


#--------------------------------------------------------------------------------------------

class DeleteUser(APIView):
    def put(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use `user_id` since that's the field available in your model
            user = User.objects.get(user_id=user_id)  # Use `user_id` instead of `id`
            user.is_active = False  # Deactivate the user
            user.user_name = f"{user_id}_Deleted-Account"  # Rename the user to indicate it's deleted
            user.email = f"{user_id}_Deleted-Account"
            user.save()  # Save the changes

            return Response({"message": "User deactivated successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------------------------------------------------------------

#-- book feature:

#-- text summarize
import json
from sumy.parsers.plaintext import PlaintextParser # pip install sumy, pip install nltk
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def summarize_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_text = data.get('text', '')

            if not selected_text:
                return JsonResponse({'error': 'No text provided for summarization.'}, status=400)

            # Parse the input text
            parser = PlaintextParser.from_string(selected_text, Tokenizer("english"))

            # Use TextRankSummarizer from sumy
            summarizer = TextRankSummarizer()
            summary_sentences = summarizer(parser.document, 2)  # Generate up to 2 summary sentences

            # Combine the sentences into a single string
            summary = ' '.join(str(sentence) for sentence in summary_sentences)

            return JsonResponse({'result': summary})

        except Exception as e:
            return JsonResponse({'error': f'Summarization failed: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


#-- translate text to arabic

import json
from googletrans import Translator  # pip install googletrans==4.0.0-rc1
from django.http import JsonResponse

# Ensure that the translate function is asynchronous
async def translate_text(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            text = data.get('text', '').strip()

            # Validate the input text
            if not text:
                return JsonResponse({'error': 'Text field is required and cannot be empty.'}, status=400)

            # Initialize the translator
            translator = Translator()

            # Await the translation as it's asynchronous
            translated_text = (await translator.translate(text, dest='ar')).text
            return JsonResponse({'result': translated_text})
        except Exception as e:
            print(f"Translation error: {e}")
            return JsonResponse({'error': 'Translation failed.'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)




#-- text to speech
from gtts import gTTS # pip install gtts (google text to speech)
from io import BytesIO
import pygame # pip install pygame
import tempfile

pygame.mixer.init()

def text_to_speech(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')

        try:
            tts = gTTS(text)
            audio_stream = BytesIO()
            tts.write_to_fp(audio_stream)
            audio_stream.seek(0)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
                temp_audio_file.write(audio_stream.read())
                temp_audio_path = temp_audio_file.name

            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()

            return JsonResponse({'message': 'Audio is playing successfully.', 'audio_url': temp_audio_path})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Failed to convert text to speech.'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def stop_text_to_speech(request):
    if request.method == 'POST':
        try:
            pygame.mixer.music.stop()
            return JsonResponse({'message': 'Audio playback stopped successfully.'})
        except Exception as e:
            print(f"Error stopping audio: {e}")
            return JsonResponse({'error': 'Failed to stop audio.'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)