from django.shortcuts import redirect
from smartlib_api.models import Manager

class ManagerLoginRequiredMixin:
    """
    A mixin to restrict access to class-based views for logged-in managers only.
    """
    def dispatch(self, request, *args, **kwargs):
        manager_id = request.session.get('manager_id')
        if not manager_id or not Manager.objects.filter(user__user_id=manager_id).exists():
            return redirect('manager_login')
        return super().dispatch(request, *args, **kwargs)
