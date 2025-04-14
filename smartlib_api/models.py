from django.db import models
from django.utils.timezone import now

# py manage.py makemigrations
# py manage.py migrate --fake

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    user_password=models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, default=now)
    @property
    def password(self):
        return self.user_password
    def get_email_field_name(self):
        return "email"
    class Meta:
        db_table = 'User'


class Reader(models.Model):
    reader_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    reader_rank = models.CharField(max_length=20, default='Rookie')
    reader_point = models.IntegerField(default=0)
    is_first_time = models.BooleanField(default=True)
    class Meta:
        db_table = 'Reader'  
        unique_together = (('reader_id', 'user'),)  


class Manager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    class Meta:
        db_table = 'Manager'
        unique_together = (('manager_id', 'user'),)  
        

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    class Meta:
        db_table = 'Category'


class Preferences(models.Model):
    preferences_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')  
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='category_id')  
    class Meta:
        db_table = 'Preferences'
        unique_together = (('preferences_id', 'reader', 'category'),) 
        
class Book(models.Model):
    class Status(models.TextChoices): #
        PENDING = 'Pending', 'Pending'
        ACCEPTED = 'Accepted', 'Accepted'
        REJECTED = 'Rejected', 'Rejected'

    book_id = models.AutoField(primary_key=True)
    book_file = models.FileField(upload_to='books/files/', null=True, blank=True)  
    book_name = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    book_type = models.CharField(max_length=255)
    book_barcode = models.CharField(max_length=255, unique=True)  
    book_image = models.FileField(upload_to='books/images/', null=True, blank=True)  
    book_reading_counter=models.IntegerField(default=0)
    book_rating_avg=models.IntegerField(default=0)
    book_uploaded_date = models.DateTimeField(default=now)
    book_favourite_counter=models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='category_id', default=1)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    book_description=models.CharField(max_length=255, default="No Description")
    class Meta:
        db_table = 'Book'
        unique_together = (('book_id', 'category'),)

class Copy_Book(models.Model):
    copy_book_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='book_id')  
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')  
    mark = models.IntegerField(default=0)
    class Meta:
        db_table = 'Copy_Book'
        unique_together = (('copy_book_id', 'book', 'reader'),)


class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    copy_book = models.ForeignKey('Copy_Book', on_delete=models.CASCADE, db_column='copy_book_id')  
    note_record = models.CharField(max_length=255)
    class Meta:
        db_table = 'Note'
        unique_together = (('note_id', 'copy_book'),)


class Gamification_Record(models.Model):
    gamification_record_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    date_and_time = models.DateTimeField(default=now)
    gamification_description = models.CharField(max_length=255)
    achieved_point = models.IntegerField(default=0)
    class Meta:
        db_table = 'Gamification_Record'
        unique_together = (('gamification_record_id', 'reader'),)


class FeedBack(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')  
    feedback_description = models.CharField(max_length=255)
    feedback_time = models.DateTimeField(null=True, default=now)

    class Meta:
        db_table = 'FeedBack'
        unique_together = (('feedback_id', 'reader'),)

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, db_column='manager_id')
    notification_record = models.CharField(max_length=255)
    notification_title = models.CharField(max_length=255, default=None)
    class Meta:
        db_table = 'Notification'
        unique_together = (('notification_id', 'reader', 'manager'),)

class Rating_And_Review(models.Model):
    rating_and_review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='book_id')
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    rating = models.IntegerField(default=0)
    review = models.CharField(max_length=255)
    class Meta:
        db_table = 'Rating_And_Review'
        unique_together = (('rating_and_review_id', 'book', 'reader'),)

class Search(models.Model):
    search_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    search_record = models.CharField(max_length=255)
    class Meta:
        db_table = 'Search'
        unique_together = (('search_id', 'reader'),)

class WishList(models.Model):
    wish_list_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='book_id')
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    class Meta:
        db_table = 'Wish_List'
        unique_together = (('wish_list_id', 'book', 'reader'),)

class BookContinueReading(models.Model):
    continue_reading_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='book_id')
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    class Meta:
        db_table = 'Book_Continue_Reading'
        unique_together = (('continue_reading_id', 'book', 'reader'),)

class UploadedBook(models.Model):
    uploaded_book_id = models.AutoField(primary_key=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='book_id')
    reader = models.ForeignKey('Reader', on_delete=models.CASCADE, db_column='reader_id')
    class Meta:
        db_table = 'Uploaded_Book'
        unique_together = (('uploaded_book_id', 'book', 'reader'),)
