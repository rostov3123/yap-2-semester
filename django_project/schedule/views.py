from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CourseForm, StudentForm, TeacherForm
from .models import Course, Student, Teacher, TeacherInfo

def teacher_list(request):
    return render(request, "schedule/teacher_list.html", {"teachers": Teacher.objects.prefetch_related("courses")})

def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save()
        TeacherInfo.objects.create(
            teacher=teacher,
            office=form.cleaned_data.get("office") or "Не указан",
            consultation_time=form.cleaned_data.get("consultation_time", ""),
        )
        return redirect("teacher_list")
    return render(request, "schedule/form.html", {"form": form, "title": "Добавить преподавателя"})

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        form.save()
        TeacherInfo.objects.update_or_create(
            teacher=teacher,
            defaults={"office": form.cleaned_data.get("office") or "Не указан", "consultation_time": form.cleaned_data.get("consultation_time", "")},
        )
        return redirect("teacher_list")
    return render(request, "schedule/form.html", {"form": form, "title": "Изменить преподавателя"})

@permission_required("schedule.delete_teacher")
def teacher_delete(request, pk):
    get_object_or_404(Teacher, pk=pk).delete()
    return redirect("teacher_list")

def course_list(request):
    teacher_id = request.GET.get("teacher")
    courses = Course.objects.select_related("teacher")
    if teacher_id:
        courses = courses.filter(teacher_id=teacher_id)
    return render(request, "schedule/course_list.html", {"courses": courses, "teachers": Teacher.objects.all()})

def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("course_list")
    return render(request, "schedule/form.html", {"form": form, "title": "Добавить курс"})

def course_update(request, pk):
    form = CourseForm(request.POST or None, instance=get_object_or_404(Course, pk=pk))
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("course_list")
    return render(request, "schedule/form.html", {"form": form, "title": "Изменить курс"})

def course_delete(request, pk):
    get_object_or_404(Course, pk=pk).delete()
    return redirect("course_list")

@login_required
def student_list(request):
    return render(request, "schedule/student_list.html", {"students": Student.objects.prefetch_related("courses")})

@login_required
def student_update(request, pk):
    form = StudentForm(request.POST or None, instance=get_object_or_404(Student, pk=pk))
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("student_list")
    return render(request, "schedule/form.html", {"form": form, "title": "Изменить студента"})

def orm_examples(request):
    context = {
        "students_without_courses": Student.objects.filter(courses=None),
        "busy_teachers": Teacher.objects.annotate(course_count=Count("courses")).filter(course_count__gt=1),
        "teachers_without_profile": Teacher.objects.filter(info__isnull=True),
    }
    return render(request, "schedule/orm_examples.html", context)
