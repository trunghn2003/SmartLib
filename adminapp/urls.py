
from django.urls import path
from .views import update_reader, search_users ,UpdateBookStatus,manager_login,logout_user
from adminapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', manager_login, name='manager_login'),
    path('logout/', logout_user, name='logout'),
    path('adminpanel/logout/', logout_user, name='logout'),




# first page 
    path('homepage', views.index, name='index'),

# categories 
    path('categories/', views.categories, name='categories'),  # Ensure this has a trailing slash
    path('add-category/', views.add_category, name='add_category'),
    path('delete-categories/', views.delete_categories, name='delete_categories'),
    path('categories-data/', views.categories_data, name='categories_data'),


#feedback
    path('feedback/', views.feedback, name='feedback'),


#user
    path('user-details/', views.user_details, name='user_details'),
    path('search-users/', search_users, name='search_users'),
    path('update-reader/', update_reader, name='update_reader'),
    path('add-user/', views.add_user, name='add_user'),
    path('deactivate-readers/<int:user_id>/', views.deactivate_reader, name='deactivate_reader'),

    
#book
    path('books/', views.book_list, name='book_list'),  # Render books.html
    path('api/categories/', views.categories_data, name='categories_data'),  # Get categories
    path('api/books/', views.get_books, name='get_books'),  # Get books with pagination
    path('api/books/<int:book_id>/', views.update_book, name='update_book'),  # Update book
    path('api/books/<int:book_id>/delete/', views.delete_book, name='delete_book'),  # Delete book
    path('api/books/add', views.add_book, name='add_book'),  # Add book




    path('notifications/', views.notificationspage, name='notifications'),
    path('api/notifibooks/<int:book_id>/', UpdateBookStatus.as_view(), name='update_book_status'),



   

    
    
    
    
    path('api/last-three-pending-books/', views.last_three_pending_books, name='last_three_pending_books'),







    

]
