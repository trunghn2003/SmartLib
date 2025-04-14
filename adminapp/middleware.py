from django.http import FileResponse
from django.conf import settings
import os

class MediaFileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.MEDIA_URL):
            media_file_path = os.path.join(settings.MEDIA_ROOT, request.path[len(settings.MEDIA_URL):])
            if os.path.exists(media_file_path):
                return FileResponse(open(media_file_path, 'rb'))
        return self.get_response(request)
