from django.db import models
from .validators import validate_course_code, validate_phone, validate_workload

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, blank=True, validators=[validate_phone])
    academic_degree = models.CharField(max_length=80, blank=True)
    workload = models.PositiveSmallIntegerField(default=0, validators=[validate_workload])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(fields=["first_name", "last_name", "email"], name="unique_teacher_identity")
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class TeacherInfo(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name="info")
    office = models.CharField(max_length=20)
    consultation_time = models.CharField(max_length=120, blank=True)
    biography = models.TextField(blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Профиль {self.teacher}"

class Course(models.Model):
    title = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True, validators=[validate_course_code])
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    description = models.TextField(blank=True)
    hours = models.PositiveSmallIntegerField(default=36)
    starts_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    group = models.CharField(max_length=20)
    courses = models.ManyToManyField(Course, related_name="students", blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email", "group"], name="unique_student_email_group")
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
