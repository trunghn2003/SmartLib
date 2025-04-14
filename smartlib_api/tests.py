from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from django.utils.timezone import now
import bcrypt
from .models import User, Reader, Gamification_Record, Notification, Book, Rating_And_Review, Category, Manager
from .views import AddRatingAndReviewView
from unittest.mock import patch, PropertyMock

# Create your tests here.
