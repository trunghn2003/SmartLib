from django.shortcuts import redirect
from django.contrib import messages
from smartlib_api.models import Manager

def manager_login_required(view_func):
    """
    A decorator to restrict access to views for logged-in managers only.
    """
    def wrapper(request, *args, **kwargs):
        # Check if the manager_id is in the session
        manager_id = request.session.get('manager_id')
        if not manager_id or not Manager.objects.filter(user__user_id=manager_id).exists():
            # Redirect to login if not logged in as a manager
            messages.error(request, "You must be logged in as a manager to access this page.")
            return redirect('manager_login')
        return view_func(request, *args, **kwargs)
    return wrapper
