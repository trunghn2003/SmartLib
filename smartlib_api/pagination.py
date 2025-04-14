from rest_framework.pagination import PageNumberPagination

class BookPagination(PageNumberPagination):
    page_size = 5  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class BookSearchPagination(PageNumberPagination):
    page_size = 4  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class WishListPagination(PageNumberPagination):
    page_size = 8  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class NotificationPagination(PageNumberPagination):
    page_size = 5  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class UploadedBookPagination(PageNumberPagination):
    page_size = 8  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class GameficationPagination(PageNumberPagination):
    page_size = 5  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size

class RatingAndReviewPagination(PageNumberPagination):
    page_size = 3  # The number of books per page
    page_size_query_param = 'page_size'  # Allows clients to modify page size