from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'        

class RatingAndReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating_And_Review
        fields = '__all__'

class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'

class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = '__all__'

class GameficationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamification_Record
        fields = '__all__'

