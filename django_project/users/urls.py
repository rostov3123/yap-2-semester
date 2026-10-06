"""Адреса профилей, регистрации и друзей."""
from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('register/',views.register,name='register'), path('',views.user_list,name='list'),
    path('<int:pk>/',views.profile,name='profile'), path('<int:pk>/edit/',views.edit_profile,name='edit'),
    path('<int:pk>/avatar/',views.avatar,name='avatar'),
    path('<int:pk>/add-friend/',views.add_friend,name='add_friend'),
    path('<int:pk>/remove-friend/',views.remove_friend,name='remove_friend'),
]
