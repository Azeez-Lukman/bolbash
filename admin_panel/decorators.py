from functools import wraps
from django.shortcuts import render, redirect
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator for views that checks if the user is authenticated AND is a staff or superuser.
    If unauthenticated, redirects to login with ?next=.
    If authenticated customer/student, renders 403 Forbidden Access Denied page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('academy:login')
            return redirect(f"{login_url}?next={request.path}")
        
        if not (request.user.is_staff or request.user.is_superuser):
            return render(request, 'admin_panel/access_denied.html', status=403)
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
