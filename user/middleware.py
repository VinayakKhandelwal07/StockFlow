# middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class ProfileUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            staff = getattr(request.user, 'staff', None)
            if staff and staff.must_update_profile:
                allowed_paths = [
                    reverse('user:profile_update'),
                    reverse('user:logout'),  # update with your actual logout view name
                ]
                if request.path not in allowed_paths:
                    return redirect('user:profile_update')
        return self.get_response(request)


# middleware.py
import threading

_user = threading.local()

def get_current_user():
    return getattr(_user, 'value', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        response = self.get_response(request)
        return response
