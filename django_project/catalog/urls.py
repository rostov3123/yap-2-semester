from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("courses/", views.courses, name="courses"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("authors/", views.authors, name="authors"),
    path("authors/<slug:slug>/", views.author_detail, name="author_detail"),
    path("info/<str:section>/", views.info, name="info"),
]
