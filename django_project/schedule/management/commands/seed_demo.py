"""Создание вымышленных данных для локальной демонстрации без очистки базы."""
from datetime import date
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from schedule.models import Teacher, TeacherInfo, Course, Student
from users.models import User

class Command(BaseCommand):
    help = 'Добавить демонстрационные данные (повторный запуск не удаляет изменения).'
    @transaction.atomic
    def handle(self,*args,**options):
        editors,_ = Group.objects.get_or_create(name='Редакторы учебной системы')
        editors.permissions.add(*Permission.objects.filter(content_type__app_label='schedule'))
        accounts = {}
        for username, first, last, phone in [
            ('editor','Анна','Волкова','+79990000001'),('student','Иван','Соколов','+79990000002'),
            ('friend','Мария','Лебедева','+79990000003'),('stranger','Павел','Морозов','+79990000004')]:
            user,created = User.objects.get_or_create(username=username,defaults={'email':f'{username}@example.org','first_name':first,'last_name':last,'phone':phone})
            if created:
                user.set_password('DemoStudy!2026');user.save()
            accounts[username]=user
        accounts['editor'].groups.add(editors)
        accounts['student'].friends.add(accounts['friend'])
        t1,_=Teacher.objects.get_or_create(email='anna.teacher@example.org',defaults={'full_name':'Анна Волкова','department':'Программирование','phone':'+79991111111','experience':8})
        TeacherInfo.objects.get_or_create(teacher=t1,defaults={'biography':'Преподаёт Python и Django.','office':'201'})
        t2,_=Teacher.objects.get_or_create(email='mikhail.teacher@example.org',defaults={'full_name':'Михаил Орлов','department':'Информационные системы','experience':5})
        TeacherInfo.objects.get_or_create(teacher=t2,defaults={'biography':'Преподаёт базы данных.','office':'305'})
        Teacher.objects.get_or_create(email='no.profile@example.org',defaults={'full_name':'Елена Миронова'})
        courses=[]
        for code,title,hours,teacher,desc in [('PY-101','Основы Python',36,t1,'Типы данных, функции и модули.'),('WEB-201','Веб-разработка на Django',48,t1,'Сайт с моделями, формами и пользователями.'),('SQL-101','Базы данных и SQL',32,t2,'Связи таблиц и запросы.')]:
            course,_=Course.objects.get_or_create(code=code,defaults={'title':title,'hours':hours,'teacher':teacher,'description':desc,'capacity':20,'start_date':date(2026,10,12),'end_date':date(2026,12,20)})
            courses.append(course)
        s1,_=Student.objects.get_or_create(email='ivan.student@example.org',defaults={'full_name':'Иван Соколов','group':'ПИ-21','enrollment_year':2025})
        s2,_=Student.objects.get_or_create(email='maria.student@example.org',defaults={'full_name':'Мария Лебедева','group':'ПИ-21','enrollment_year':2025})
        Student.objects.get_or_create(email='pavel.student@example.org',defaults={'full_name':'Павел Морозов','group':'ПИ-22'})
        s1.courses.add(courses[0],courses[1]);s2.courses.add(courses[0])
        self.stdout.write(self.style.SUCCESS('Демо-данные готовы. Новые аккаунты: editor, student, friend, stranger. Пароль: DemoStudy!2026'))
