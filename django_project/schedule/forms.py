"""Обычная форма ЛР3 и ModelForm с валидацией ЛР4."""
from django import forms
from django.db import transaction
from .models import Teacher, TeacherInfo, Course, Student
from .validators import validate_person_name

class TeacherForm(forms.Form):
    """Сохранённый этап ЛР3: явные label, help_text, placeholder."""
    full_name = forms.CharField(label='ФИО', max_length=150, validators=[validate_person_name], help_text='Имя и фамилия преподавателя.', widget=forms.TextInput(attrs={'placeholder':'Анна Волкова'}))
    email = forms.EmailField(label='Email', help_text='Уникальный адрес для связи.', widget=forms.EmailInput(attrs={'placeholder':'teacher@example.org'}))
    department = forms.CharField(label='Кафедра', required=False, max_length=120, help_text='Необязательное поле.', widget=forms.TextInput(attrs={'placeholder':'Программирование'}))
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Teacher.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Преподаватель с таким email уже существует.')
        return email

# Исходное имя класса из задания ЛР3; рабочие ModelForm находятся ниже.
BasicTeacherForm = TeacherForm

class TeacherModelForm(forms.ModelForm):
    biography = forms.CharField(label='Биография', required=False, widget=forms.Textarea(attrs={'rows':3}))
    office = forms.CharField(label='Кабинет', required=False, max_length=30)
    class Meta:
        model = Teacher
        fields = ['full_name','email','department','phone','experience','biography','office']
        widgets = {'full_name': forms.TextInput(attrs={'placeholder':'Анна Волкова'}), 'phone': forms.TextInput(attrs={'placeholder':'+79991234567'})}
        help_texts = {'experience':'От 0 до 60 лет.', 'department':'Укажите кафедру, если назначен кабинет.'}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            info = TeacherInfo.objects.filter(teacher=self.instance).first()
            if info:
                self.initial.update(biography=info.biography, office=info.office)
    def clean_full_name(self):
        return ' '.join(self.cleaned_data['full_name'].split())
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Teacher.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот email уже занят.')
        return email
    def clean(self):
        data = super().clean()
        if data.get('office') and not data.get('department'):
            self.add_error('department', 'Для кабинета необходимо указать кафедру.')
        return data
    @transaction.atomic
    def save(self, commit=True):
        if not commit:
            raise ValueError('Связанный профиль сохраняется только вместе с преподавателем.')
        teacher = super().save()
        TeacherInfo.objects.update_or_create(teacher=teacher, defaults={key:self.cleaned_data[key] for key in ['biography','office']})
        return teacher

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code','title','description','teacher','hours','start_date','end_date','capacity']
        widgets = {'description':forms.Textarea(attrs={'rows':3}), 'start_date':forms.DateInput(attrs={'type':'date'},format='%Y-%m-%d'), 'end_date':forms.DateInput(attrs={'type':'date'},format='%Y-%m-%d')}
    def clean_title(self):
        value = ' '.join(self.cleaned_data['title'].split())
        if len(value) < 4:
            raise forms.ValidationError('Название должно содержать минимум 4 символа.')
        return value
    def clean(self):
        data = super().clean()
        start, end = data.get('start_date'), data.get('end_date')
        if bool(start) != bool(end):
            raise forms.ValidationError('Укажите обе даты или оставьте обе пустыми.')
        if start and end and end < start:
            self.add_error('end_date','Окончание не может быть раньше начала.')
        if self.instance.pk and data.get('capacity', 0) < self.instance.students.count():
            self.add_error('capacity','Вместимость меньше числа записанных студентов.')
        return data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name','email','group','enrollment_year']
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Student.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот email уже занят.')
        return email
    def clean_group(self):
        return self.cleaned_data['group'].strip().upper()

class EnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Курс')
