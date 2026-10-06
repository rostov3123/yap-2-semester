"""Корневые маршруты и стандартные обработчики ошибок."""
from django.contrib import admin
from django.urls import include, path
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('schedule/', include('schedule.urls')),
    path('', include('catalog.urls')),
]
handler404 = 'catalog.views.not_found'
handler403 = 'catalog.views.forbidden'
