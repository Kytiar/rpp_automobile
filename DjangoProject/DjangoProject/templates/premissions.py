# blog/permissions.py
from django.core.exceptions import PermissionDenied

def admin_or_author_required(view_func):
    """Только администраторы или авторы поста"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_author_or_editor_required(view_func):
    """Администраторы, авторы или редакторы"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper