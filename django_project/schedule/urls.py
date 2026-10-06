"""Маршруты учебной системы."""
from django.urls import path
from . import views
app_name = 'schedule'
urlpatterns = [
    path('teachers/',views.teachers,name='teachers'),
    path('teachers/add/',views.teacher_create,name='teacher_create'),
    path('teachers/add-basic/',views.teacher_basic,name='teacher_basic'),
    path('teachers/<int:pk>/',views.teacher_detail,name='teacher_detail'),
    path('teachers/<int:pk>/edit/',views.teacher_update,name='teacher_update'),
    path('teachers/<int:pk>/delete/',views.teacher_delete,name='teacher_delete'),
    path('courses/',views.courses,name='courses'),
    path('courses/add/',views.course_create,name='course_create'),
    path('courses/<int:pk>/edit/',views.course_update,name='course_update'),
    path('courses/<int:pk>/delete/',views.course_delete,name='course_delete'),
    path('students/',views.students,name='students'),
    path('students/add/',views.student_create,name='student_create'),
    path('students/<int:pk>/edit/',views.student_update,name='student_update'),
    path('students/<int:pk>/delete/',views.student_delete,name='student_delete'),
    path('students/<int:pk>/enroll/',views.enroll,name='enroll'),
    path('students/<int:pk>/unenroll/<int:course_pk>/',views.unenroll,name='unenroll'),
    path('orm/',views.orm_examples,name='orm'),
]
