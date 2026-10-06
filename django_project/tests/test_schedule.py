"""CRUD, формы, ограничения БД, связи и ORM."""
import pytest
from django.db import IntegrityError,transaction
from django.urls import reverse
from schedule.models import Teacher,TeacherInfo,Course,Student
from schedule.forms import TeacherModelForm,CourseForm
pytestmark=pytest.mark.django_db


def teacher_data():
    return {'full_name':'Елена Миронова','email':'elena@example.org','department':'ИТ','phone':'+79991234567','experience':3,'biography':'Текст','office':'102'}


def course_data(teacher):
    return {'code':'WEB-202','title':'Разработка сайтов','teacher':teacher.pk,'hours':40,'capacity':20,'start_date':'2026-10-10','end_date':'2026-12-01'}

@pytest.mark.parametrize('route',['teacher_create','course_create','student_create','teacher_basic'])
def test_permissions(client,user,route):
    client.force_login(user)
    assert client.get(reverse('schedule:'+route)).status_code==403
    assert client.post(reverse('schedule:'+route),{}).status_code==403


def test_teacher_create_update_delete(client,editor,course):
    client.force_login(editor)
    response=client.post(reverse('schedule:teacher_create'),teacher_data())
    assert response.status_code==302
    obj=Teacher.objects.get(email='elena@example.org')
    assert obj.info.office=='102'
    data=teacher_data();data['office']='103';data['biography']='Изменено'
    response=client.post(reverse('schedule:teacher_update',args=[obj.pk]),data)
    assert response.status_code==302
    obj.info.refresh_from_db();assert obj.info.biography=='Изменено'
    Course.objects.filter(pk=course.pk).update(teacher=obj)
    delete=reverse('schedule:teacher_delete',args=[obj.pk])
    assert client.get(delete).status_code==200 and Teacher.objects.filter(pk=obj.pk).exists()
    assert client.post(delete).status_code==302
    assert not TeacherInfo.objects.filter(teacher_id=obj.pk).exists()
    course.refresh_from_db();assert course.teacher is None


def test_basic_form(client,editor):
    client.force_login(editor)
    response=client.post(reverse('schedule:teacher_basic'),{'full_name':'Ольга Миронова','email':'olga@example.org'})
    assert response.status_code==302
    assert Teacher.objects.get(email='olga@example.org').info
    response=client.post(reverse('schedule:teacher_basic'),{'full_name':'Ольга Миронова','email':'olga@example.org'})
    assert 'email' in response.context['form'].errors

@pytest.mark.parametrize('change,field',[({'full_name':'123'},'full_name'),({'phone':'8abc'},'phone'),({'experience':61},'experience'),({'department':''},'department')])
def test_teacher_validation(change,field):
    data=teacher_data();data.update(change)
    form=TeacherModelForm(data)
    assert not form.is_valid() and field in form.errors

@pytest.mark.parametrize('change,field',[({'code':'wrong'},'code'),({'title':'ab'},'title'),({'hours':0},'hours'),({'capacity':0},'capacity'),({'end_date':'2026-01-01'},'end_date'),({'end_date':''},'__all__')])
def test_course_validation(teacher,change,field):
    data=course_data(teacher);data.update(change)
    form=CourseForm(data)
    assert not form.is_valid() and field in form.errors


def test_course_crud(client,editor,teacher):
    client.force_login(editor)
    data=course_data(teacher)
    assert client.post(reverse('schedule:course_create'),data).status_code==302
    obj=Course.objects.get(code=data['code'])
    data['title']='Новое название'
    assert client.post(reverse('schedule:course_update',args=[obj.pk]),data).status_code==302
    obj.refresh_from_db();assert obj.title=='Новое название'
    assert client.post(reverse('schedule:course_delete',args=[obj.pk])).status_code==302
    assert not Course.objects.filter(pk=obj.pk).exists()


def test_student_crud(client,editor):
    client.force_login(editor)
    data={'full_name':'Иван Соколов','email':'new@example.org','group':'пи-22','enrollment_year':2026}
    assert client.post(reverse('schedule:student_create'),data).status_code==302
    obj=Student.objects.get(email=data['email']);assert obj.group=='ПИ-22'
    data['group']='ПИ-23'
    assert client.post(reverse('schedule:student_update',args=[obj.pk]),data).status_code==302
    obj.refresh_from_db();assert obj.group=='ПИ-23'
    assert client.post(reverse('schedule:student_delete',args=[obj.pk])).status_code==302
    assert not Student.objects.filter(pk=obj.pk).exists()


def test_enroll_duplicate_capacity_and_unenroll(client,editor,course,student):
    client.force_login(editor)
    course.capacity=1;course.save()
    url=reverse('schedule:enroll',args=[student.pk])
    assert client.post(url,{'course':course.pk}).status_code==302
    assert student.courses.count()==1
    assert 'course' in client.post(url,{'course':course.pk}).context['form'].errors
    other=Student.objects.create(full_name='Олег Соколов',email='other@example.org',group='ПИ-21')
    response=client.post(reverse('schedule:enroll',args=[other.pk]),{'course':course.pk})
    assert 'course' in response.context['form'].errors and not other.courses.exists()
    url=reverse('schedule:unenroll',args=[student.pk,course.pk])
    assert client.get(url).status_code==405
    assert client.post(url).status_code==302 and not student.courses.exists()


def test_db_constraints(course):
    with pytest.raises(IntegrityError),transaction.atomic():
        Course.objects.filter(pk=course.pk).update(hours=0)
    with pytest.raises(IntegrityError),transaction.atomic():
        Course.objects.filter(pk=course.pk).update(start_date='2026-12-01',end_date='2026-01-01')
    with pytest.raises(IntegrityError),transaction.atomic():
        Course.objects.create(code=course.code,title='Повтор',hours=30)


def test_filter_and_orm(client,user,course,student):
    client.force_login(user)
    student.courses.add(course)
    response=client.get(reverse('schedule:courses'),{'teacher':course.teacher_id})
    assert list(response.context['courses'])==[course]
    response=client.get(reverse('schedule:orm'),{'n':0,'course':course.pk})
    assert list(response.context['course_students'])==[student]
    assert list(response.context['busy_teachers'])==[course.teacher]
    assert list(response.context['free_students'])==[]
    Teacher.objects.create(full_name='Без Профиля',email='noprofile@example.org')
    assert client.get(reverse('schedule:orm')).context['no_profile'].count()==1


def test_empty_post_basic_has_errors(client,editor):
    client.force_login(editor)
    response=client.post(reverse('schedule:teacher_basic'),{})
    assert response.context['form'].is_bound
    assert 'full_name' in response.context['form'].errors
