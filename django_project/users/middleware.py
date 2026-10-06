"""Анонимам доступны только регистрация и маршруты аутентификации."""
from django.contrib.auth.views import redirect_to_login
from django.urls import resolve, Resolver404

class MemberAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if not request.user.is_authenticated:
            try:
                name = resolve(request.path_info).view_name
            except Resolver404:
                name = None
            public = {'users:register', 'login', 'password_reset', 'password_reset_done',
                      'password_reset_confirm', 'password_reset_complete', 'admin:login'}
            if name not in public and not request.path.startswith('/static/'):
                return redirect_to_login(request.get_full_path())
        return self.get_response(request)
