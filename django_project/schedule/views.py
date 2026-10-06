"""CRUD учебной системы. Изменения требуют разрешений и POST с CSRF."""
import logging
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import BasicTeacherForm, TeacherModelForm, CourseForm, StudentForm, EnrollmentForm
from .models import Teacher, TeacherInfo, Course, Student
logger = logging.getLogger(__name__)


def teachers(request):
    return render(request,'schedule/teachers.html',{'teachers':Teacher.objects.prefetch_related('courses')})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher.objects.prefetch_related('courses'),pk=pk)
    return render(request,'schedule/teacher_detail.html',{'teacher':teacher,'info':TeacherInfo.objects.filter(teacher=teacher).first()})

@permission_required('schedule.add_teacher',raise_exception=True)
def teacher_basic(request):
    form = BasicTeacherForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            teacher = Teacher.objects.create(**form.cleaned_data)
            TeacherInfo.objects.create(teacher=teacher)
        return redirect('schedule:teacher_detail',pk=teacher.pk)
    return render(request,'form.html',{'form':form,'title':'Добавить преподавателя · простая форма'})


def edit_object(request, form_class, instance, title, destination):
    form = form_class(request.POST if request.method == 'POST' else None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        logger.info('Сохранён %s id=%s user_id=%s', obj.__class__.__name__,obj.pk,request.user.pk)
        messages.success(request,'Изменения сохранены.')
        return redirect(destination)
    return render(request,'form.html',{'form':form,'title':title})

@permission_required('schedule.add_teacher',raise_exception=True)
def teacher_create(request):
    return edit_object(request,TeacherModelForm,None,'Добавить преподавателя','schedule:teachers')

@permission_required('schedule.change_teacher',raise_exception=True)
def teacher_update(request,pk):
    return edit_object(request,TeacherModelForm,get_object_or_404(Teacher,pk=pk),'Изменить преподавателя','schedule:teachers')


def delete_object(request,obj,destination):
    if request.method == 'POST':
        logger.info('Удалён %s id=%s user_id=%s',obj.__class__.__name__,obj.pk,request.user.pk)
        obj.delete()
        messages.success(request,'Запись удалена.')
        return redirect(destination)
    return render(request,'confirm_delete.html',{'object':obj})

@permission_required('schedule.delete_teacher',raise_exception=True)
def teacher_delete(request,pk):
    return delete_object(request,get_object_or_404(Teacher,pk=pk),'schedule:teachers')


def courses(request):
    items = Course.objects.select_related('teacher').annotate(student_count=Count('students'))
    teacher_id = request.GET.get('teacher','')
    error = ''
    if teacher_id:
        if teacher_id.isdecimal():
            items = items.filter(teacher_id=int(teacher_id))
        else:
            items = items.none();error='Выберите преподавателя из списка.'
    return render(request,'schedule/courses.html',{'courses':items,'teachers':Teacher.objects.all(),'selected':teacher_id,'error':error})

@permission_required('schedule.add_course',raise_exception=True)
def course_create(request):
    return edit_object(request,CourseForm,None,'Добавить курс','schedule:courses')

@permission_required('schedule.change_course',raise_exception=True)
def course_update(request,pk):
    return edit_object(request,CourseForm,get_object_or_404(Course,pk=pk),'Изменить курс','schedule:courses')

@permission_required('schedule.delete_course',raise_exception=True)
def course_delete(request,pk):
    return delete_object(request,get_object_or_404(Course,pk=pk),'schedule:courses')


def students(request):
    return render(request,'schedule/students.html',{'students':Student.objects.prefetch_related('courses')})

@permission_required('schedule.add_student',raise_exception=True)
def student_create(request):
    return edit_object(request,StudentForm,None,'Добавить студента','schedule:students')

@permission_required('schedule.change_student',raise_exception=True)
def student_update(request,pk):
    return edit_object(request,StudentForm,get_object_or_404(Student,pk=pk),'Изменить студента','schedule:students')

@permission_required('schedule.delete_student',raise_exception=True)
def student_delete(request,pk):
    return delete_object(request,get_object_or_404(Student,pk=pk),'schedule:students')

@permission_required('schedule.change_student',raise_exception=True)
def enroll(request,pk):
    student = get_object_or_404(Student,pk=pk)
    form = EnrollmentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            course = Course.objects.select_for_update().get(pk=form.cleaned_data['course'].pk)
            if student.courses.filter(pk=course.pk).exists():
                form.add_error('course','Студент уже записан на этот курс.')
            elif course.students.count() >= course.capacity:
                form.add_error('course','Свободных мест нет.')
            else:
                student.courses.add(course)
                messages.success(request,'Студент записан на курс.')
                return redirect('schedule:students')
    return render(request,'form.html',{'form':form,'title':f'Записать на курс: {student}'})

@permission_required('schedule.change_student',raise_exception=True)
@require_POST
def unenroll(request,pk,course_pk):
    student = get_object_or_404(Student,pk=pk)
    course = get_object_or_404(Course,pk=course_pk)
    student.courses.remove(course)
    return redirect('schedule:students')


def orm_examples(request):
    raw = request.GET.get('n','1')
    n = int(raw) if raw.isdecimal() and len(raw)<6 else 1
    course_pk = request.GET.get('course','')
    course_students = Student.objects.filter(courses__pk=course_pk) if course_pk.isdecimal() else Student.objects.none()
    return render(request,'schedule/orm.html',{
        'n':n,'courses':Course.objects.all(),'selected':course_pk,'course_students':course_students,
        'busy_teachers':Teacher.objects.annotate(total=Count('courses')).filter(total__gt=n),
        'free_students':Student.objects.filter(courses__isnull=True),
        'no_profile':Teacher.objects.filter(info__isnull=True),
    })
