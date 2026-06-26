from django import forms
from .models import Course, Student, Teacher, TeacherInfo

class TeacherForm(forms.ModelForm):
    office = forms.CharField(label="Кабинет", max_length=20, required=False, help_text="Например: 301")
    consultation_time = forms.CharField(label="Консультации", required=False)

    class Meta:
        model = Teacher
        fields = ["first_name", "last_name", "email", "phone", "academic_degree", "workload", "is_active"]
        labels = {"first_name": "Имя", "last_name": "Фамилия"}
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "teacher@example.com"})}

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not email.endswith((".ru", ".com", ".edu")):
            raise forms.ValidationError("Нужен домен .ru, .com или .edu")
        return email

    def clean_workload(self):
        workload = self.cleaned_data["workload"]
        if workload % 2:
            raise forms.ValidationError("Нагрузка должна быть четным числом")
        return workload

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        return phone.replace(" ", "")

    def clean(self):
        data = super().clean()
        if data.get("is_active") and data.get("workload", 0) == 0:
            raise forms.ValidationError("Активному преподавателю нужна нагрузка")
        return data

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "code", "teacher", "description", "hours", "starts_at"]
        widgets = {"starts_at": forms.DateInput(attrs={"type": "date"})}

    def clean_hours(self):
        hours = self.cleaned_data["hours"]
        if hours < 8:
            raise forms.ValidationError("Курс должен быть не короче 8 часов")
        return hours

    def clean(self):
        data = super().clean()
        teacher = data.get("teacher")
        if teacher and not teacher.is_active:
            raise forms.ValidationError("Нельзя назначить неактивного преподавателя")
        return data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email", "group", "courses"]
        widgets = {"courses": forms.CheckboxSelectMultiple}

class TeacherInfoForm(forms.ModelForm):
    class Meta:
        model = TeacherInfo
        fields = ["office", "consultation_time", "biography", "experience_years"]
