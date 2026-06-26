from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile, name="profile_detail"),
    path("all/", views.user_list, name="user_list"),
    path("friends/add/<int:pk>/", views.add_friend, name="add_friend"),
    path("friends/remove/<int:pk>/", views.remove_friend, name="remove_friend"),
]
