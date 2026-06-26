from django.urls import path
from . import views

urlpatterns = [
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/create/", views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/update/", views.teacher_update, name="teacher_update"),
    path("teachers/<int:pk>/delete/", views.teacher_delete, name="teacher_delete"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/create/", views.course_create, name="course_create"),
    path("courses/<int:pk>/update/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("students/", views.student_list, name="student_list"),
    path("students/<int:pk>/update/", views.student_update, name="student_update"),
    path("orm/", views.orm_examples, name="orm_examples"),
]
