import threading
from django.utils.deprecation import MiddlewareMixin

_local_storage = threading.local()

class CurrentRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _local_storage.request = request

def get_current_request():
    return getattr(_local_storage, "request", None)

def get_current_user():
    request = get_current_request()
    if request is None:
        return None
    return getattr(request, "user", None)