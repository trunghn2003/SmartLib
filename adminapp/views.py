
#------------------------------------------
#import and from
import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from sympy import Q
from smartlib_api.models import  Book, Category, FeedBack, Reader, User, Notification, UploadedBook
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from .decorators import manager_login_required

#------------------------------------------#------------------------------------------#------------------------------------------


#fisrt page
@manager_login_required
def index(request):
    return render(request, 'homepage/index.html')
#------------------------------------------#------------------------------------------#------------------------------------------


# all views for categories (get data , add , delete )
#get data
@manager_login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories/categories.html', {'categories': categories})



@csrf_exempt
def add_category(request):
    """Handle adding a new category."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('category_name')

            if not category_name:
                return JsonResponse({'status': 'error', 'message': 'Category name is required.'}, status=400)

            # Check if the category already exists
            if Category.objects.filter(category_name=category_name).exists():
                return JsonResponse({'status': 'error', 'message': 'Category already exists.'}, status=400)

            # Create the new category
            category = Category.objects.create(category_name=category_name)
            return JsonResponse({'status': 'success', 'message': 'Category added successfully!', 'category_id': category.category_id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



# delete
@csrf_exempt
def delete_categories(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_ids = data.get('category_ids', [])

            if not category_ids:
                return JsonResponse({'status': 'error', 'message': 'No categories selected for deletion.'}, status=400)

            Category.objects.filter(category_id__in=category_ids).delete()
            return JsonResponse({'status': 'success', 'message': 'Selected categories deleted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
#------------------------------------------#------------------------------------------#------------------------------------------

@manager_login_required
def feedback(request):
    # Fetch all feedback data
    feedbacks = FeedBack.objects.all().select_related('reader__user')
    paginator = Paginator(feedbacks, 2)  # Display 2 feedbacks per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX Request
        feedback_list = [
            {
                'user_name': feedback.reader.user.user_name,
                'feedback_description': feedback.feedback_description,
                'feedback_time': feedback.feedback_time.strftime('%Y-%m-%d %H:%M:%S') if feedback.feedback_time else 'N/A'
            }
            for feedback in page_obj
        ]
        return JsonResponse({
            'feedbacks': feedback_list,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

    return render(request, 'feedback/feedback.html', {'feedbacks': page_obj})
#------------------------------------------#------------------------------------------#------------------------------------------


@manager_login_required
def user_details(request):
    query = request.GET.get('query', '').strip()  # Get and trim the search query
    if query:
        # Filter readers by username or email if a query exists
        readers = Reader.objects.filter(
            Q(user__user_name__icontains=query) | Q(user__email__icontains=query)
        ).select_related('user')
    else:
        # Fetch all readers if no query
        readers = Reader.objects.select_related('user').all()

    # Paginate the readers, 3 per page
    paginator = Paginator(readers, 3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Render the template with paginated and filtered data
    return render(request, 'user_details/user_details.html', {
        'readers': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    })

@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('user_name')
            email = data.get('email')
            password = data.get('password')

            is_active = False  # Set default value for is_active
            reader_rank = data.get('reader_rank', 'Rookie')
            reader_points = data.get('reader_points', 0)

            if not user_name or not email or not password:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

            # Check if the email already exists in the User table
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already exists in the database.'}, status=400)

            # Create the User
            user = User.objects.create(
                user_name=user_name,
                email=email,
                user_password=make_password(password),
                is_active=is_active
            )

            # Create the Reader
            reader = Reader.objects.create(
                user=user,
                reader_rank=reader_rank,
                reader_point=reader_points
            )

            return JsonResponse({'status': 'success', 'message': 'User and Reader added successfully!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



@csrf_exempt
@require_http_methods(["POST"])
def deactivate_reader(request, user_id):
    try:
        user = get_object_or_404(User, user_id=user_id)

        user.is_active = False
        user.user_name = f"{user_id}_Deleted-Account"
        user.email = f"{user_id}_Deleted-Account"
        user.last_login = datetime.now()
        user.save()

        try:
            reader = Reader.objects.get(user=user)
            reader.reader_rank = 'Rookie'
            reader.reader_point = 0
            reader.is_first_time = True
            reader.save()
        except Reader.DoesNotExist:
            pass

        return JsonResponse({"status": "success", "message": "User and reader deactivated successfully!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# search for user (reader)
def search_users(request):
    query = request.GET.get("query", "").strip()
    readers = Reader.objects.select_related('user')

    if query:
        readers = readers.filter(user__user_name__icontains=query)

    paginator = Paginator(readers, 3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_details/user_details.html', {
        'readers': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    })



@csrf_exempt
@require_http_methods(["POST"])
def update_reader(request):
    try:
        data = json.loads(request.body)
        reader_id = data.get('reader_id')
        field = data.get('field')
        value = data.get('value')

        if not reader_id or not field or value is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid input'})

        # Fetch the reader
        reader = get_object_or_404(Reader, user_id=reader_id)

        # Handle reader-specific fields
        if field in ['reader_rank', 'reader_point', 'is_first_time']:
            if field == 'reader_rank' and value not in ['Rookie','Bronze', 'Silver', 'Gold']:
                return JsonResponse({'status': 'error', 'message': 'Invalid rank value'}, status=400)

            if field == 'reader_point':
                try:
                    value = int(value)  # Ensure point is an integer
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Points must be an integer'}, status=400)

            setattr(reader, field, value)
            reader.save()
            return JsonResponse({'status': 'success', 'message': f'{field} updated successfully'})

        # Handle user-specific fields
        user = reader.user
        if field in ['user_name', 'email', 'is_active']:
            if field == 'is_active':
                if isinstance(value, str):  # Convert string 'true'/'false' to boolean
                    value = value.lower() == 'true'
                elif not isinstance(value, bool):
                    return JsonResponse({'status': 'error', 'message': 'Invalid value for is_active'}, status=400)

            setattr(user, field, value)
            user.save()
            return JsonResponse({'status': 'success', 'message': f'{field} updated successfully'})

        # If the field is not recognized
        return JsonResponse({'status': 'error', 'message': 'Invalid field for update'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        # Log error details
        return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'}, status=500)

#------------------------------------------#------------------------------------------#------------------------------------------




def get_last_three_pending_books():
    pending_books = Book.objects.filter(status=Book.Status.PENDING).order_by('-book_uploaded_date')[:3]
    return pending_books


from django.http import JsonResponse

def last_three_pending_books(request):
    pending_books = Book.objects.filter(status=Book.Status.PENDING).order_by('-book_uploaded_date')[:3]
    data = [
        {
            "book_name": book.book_name,
            "book_author": book.book_author,
            "book_uploaded_date": book.book_uploaded_date,
        }
        for book in pending_books
    ]
    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

@method_decorator(csrf_exempt, name='dispatch')
class UpdateBookStatus(View):
    def patch(self, request, book_id):
        try:
            book = Book.objects.get(pk=book_id)
            data = json.loads(request.body)
            status = data.get('status')

            if status not in ['Accepted', 'Rejected']:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            book.status = status
            book.save()

            uploadedBook = UploadedBook.objects.filter(book_id=book_id).first()

            if book.status == 'Accepted':
                Notification.objects.create(
                    reader_id=uploadedBook.reader_id,
                    manager_id=2,
                    notification_record="your book now is uploaded in SmartLib library.",
                    notification_title="Accept Uploaded Book",
                )
            elif book.status == 'Rejected':
                Notification.objects.create(
                    reader_id=uploadedBook.reader_id,
                    manager_id=2,
                    notification_record="your book dosn't meet SmartLib standards and conditions.",
                    notification_title="Rejected Uploaded Book",
                )

            return JsonResponse({'message': 'Book status updated successfully.'})
        except Book.DoesNotExist:
            return JsonResponse({'error': 'Book not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)










from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_user(request):
    # Log out the user and clear the session
    logout(request)  # Clears the session
    return redirect('manager_login')  # Redirect to the login page



















# get category for book
def categories_data(request):

    categories = Category.objects.values('category_id', 'category_name')
    return JsonResponse({'categories': list(categories)})









from django.shortcuts import render, redirect
from django.contrib import messages
from smartlib_api.models import User, Manager
import bcrypt

from django.http import HttpResponseRedirect


def manager_login(request):
    if request.method == "POST":
        username = request.POST.get('username')  # Get username from POST data
        password = request.POST.get('password')  # Get password from POST data
        # print(User.objects.get(email=username))
        print(username, password)
        try:
            # Check if user exists with the given username
            user = User.objects.get(email=username)

            # Check if the password matches
            if bcrypt.checkpw(password.encode('utf-8'), user.user_password.encode('utf-8')):
                # Ensure the user is a manager
                if Manager.objects.filter(user=user).exists():
                    # Login successful
                    request.session['manager_id'] = user.user_id  # Save manager ID in session
                    # Redirect to the homepage index
                    return redirect('index')  # Use the name of the path
                else:
                    messages.error(request, "You are not authorized as a manager.")
            else:
                messages.error(request, "Invalid username or password.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'login/login.html')  # Render login page for GET request or invalid login






# Get category for book
def categories_data(request):
    categories = Category.objects.values('category_id', 'category_name')
    return JsonResponse({'categories': list(categories)})

# Render books.html page
@manager_login_required
def book_list(request):
    """
    View to render the HTML page for books.
    """
    return render(request, 'books/books.html')

# API to fetch books with pagination
def get_books(request):
    """
    API endpoint to fetch books with pagination.
    """
    page_number = int(request.GET.get('page', 1))
    books_per_page = int(request.GET.get('limit',4))

    books = Book.objects.select_related('category').only(
        'book_description',
        'book_image',
        'book_barcode',
        'book_author',
        'book_name',
        'book_file',
        'status',
        'category__category_name'
    )
    paginator = Paginator(books, books_per_page)
    page_books = paginator.get_page(page_number)

    books_data = [{
        'book_id': book.book_id,
        'book_name': book.book_name,
        'book_author': book.book_author,
        'book_barcode': book.book_barcode,
        'book_description': book.book_description,
        'category_name': book.category.category_name,
        'status': book.status,
        'book_image': book.book_image.url if book.book_image else None,
    } for book in page_books]

    return JsonResponse({
        'books': books_data,
        'total': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_books.number,
    })

# Update the book
@csrf_exempt
def update_book(request, book_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)  # Parse JSON request body
            book = get_object_or_404(Book, pk=book_id)

            # Update category by category_name
            if 'category_name' in data:
                category_name = data['category_name']
                category = get_object_or_404(Category, category_name=category_name)
                book.category = category

            # Update other fields dynamically
            for field, value in data.items():
                if field != 'category_name' and hasattr(book, field):
                    setattr(book, field, value)

            book.save()
            return JsonResponse({'status': 'success', 'message': 'Book updated successfully!'})
        except Category.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'Category with name {data["category_name"]} does not exist.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



@csrf_exempt
def delete_book(request, book_id):
    if request.method == 'DELETE':
        try:
            print(f"Attempting to delete book with ID: {book_id}")  # Log book ID
            book = get_object_or_404(Book, book_id=book_id)
            book.delete()
            print(f"Book with ID {book_id} deleted successfully.")  # Log success
            return JsonResponse({'status': 'success', 'message': 'Book deleted successfully!'})
        except Book.DoesNotExist:
            print(f"Book with ID {book_id} not found.")  # Log book not found
            return JsonResponse({'status': 'error', 'message': f'Book with ID {book_id} not found.'}, status=404)
        except Exception as e:
            print(f"Error deleting book with ID {book_id}: {str(e)}")  # Log exception details
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    print("Invalid request method.")  # Log invalid method
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
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

            # Log the data for debugging
            print("POST data:", request.POST)
            print("FILES data:", request.FILES)

            # Validate required fields
            if not all([book_name, book_author, book_barcode, book_description, category_id, book_file, book_image]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

            # Validate category
            category = Category.objects.filter(category_id=category_id).first()
            if not category:
                return JsonResponse({'status': 'error', 'message': 'Invalid category.'}, status=400)

            # Save the book without file and image to get the book ID
            book = Book.objects.create(
                book_name=book_name,
                book_author=book_author,
                book_barcode=book_barcode,
                book_description=book_description,
                category=category,
                book_reading_counter=0,
                book_rating_avg=0,
                book_favourite_counter=0,
                status=Book.Status.ACCEPTED,
                book_uploaded_date=now()
            )

            # Rename and save the book file
            book_file_extension = book_file.name.split('.')[-1]
            book_file_name = f"{book.book_id}_file.{book_file_extension}"
            book.book_file.save(book_file_name, book_file)

            # Rename and save the book image
            book_image_extension = book_image.name.split('.')[-1]
            book_image_name = f"{book.book_id}_image.{book_image_extension}"
            book.book_image.save(book_image_name, book_image)

            # Save the book instance with updated file paths
            book.save()

            return JsonResponse({'status': 'success', 'message': 'Book added successfully!', 'book_id': book.book_id})

        except Exception as e:
            # Log the exception
            print("Error occurred:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@manager_login_required
def notificationspage(request):
    # Fetch all books with 'Pending' status, ordered by uploaded date
    pending_books = Book.objects.filter(status=Book.Status.PENDING).order_by('-book_uploaded_date')

    context = {
        'books': pending_books,  # Pass all pending books to the template
    }

    return render(request, 'notifications/notifications.html', context)
