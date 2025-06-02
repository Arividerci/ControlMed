import datetime
from datetime import date
from django import forms
from django.contrib.auth.models import User
from .models import Patient, MedicalStaff, Hospitalization, Purpose, Procedures, Medication, ProceduresExecution, MedicationDispensing


from django.core.exceptions import ValidationError


class HospitalizationForm(forms.ModelForm):
    hospitalization_startdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today
    )
    hospitalization_enddate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = Hospitalization
        fields = ['hospitalization_room', 'hospitalization_startdate', 'hospitalization_enddate']

class AddPatientForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('мужской', 'Мужской'),
        ('женский', 'Женский'),
    ]

    BLOOD_TYPE_CHOICES = [
        ('O-', 'O-'), ('O+', 'O+'),
        ('A-', 'A-'), ('A+', 'A+'),
        ('B-', 'B-'), ('B+', 'B+'),
        ('AB-', 'AB-'), ('AB+', 'AB+'),
    ]

    patient_gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Пол')
    patient_blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, label='Группа крови')

    class Meta:
        model = Patient
        fields = [
            'patient_name',
            'patient_birthday',
            'patient_gender',
            'patient_weight',
            'patient_height',
            'patient_blood_type',
            'patient_photo',
        ]
        widgets = {
            'patient_birthday': forms.DateInput(attrs={'type': 'date'}),
        }

        labels = {
            'patient_name': 'ФИО',
            'patient_birthday': 'Дата рождения',
            'patient_weight': 'Вес',
            'patient_height': 'Рост',
            'patient_photo': 'Фото пациента',
        }

class RegisterStep1Form(forms.Form):
    username = forms.CharField(max_length=150, label="Логин (например, s10361784ms)")
    email = forms.EmailField(label='Почта')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        email = cleaned_data.get("email")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("Пароли не совпадают.")

        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return username

class PurposeForm(forms.ModelForm):
    purpose_startdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата начала'
    )

    class Meta:
        model = Purpose
        fields = [
            'purpose_startdate',
            'purpose_duration',
            'purpose_status',
            'purpose_diagnosis',
            # 👇 не включаем medical_staff и hospitalization
        ]
        widgets = {
            'purpose_diagnosis': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'purpose_duration': 'Длительность (дней)',
            'purpose_status': 'Статус',
            'purpose_diagnosis': 'Диагноз / комментарий',
        }
        
class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class RegisterStep2Form(forms.ModelForm):
    GENDER_CHOICES = [
        ('муж', 'Мужской'),
        ('жен', 'Женский'),
    ]

    POST_CHOICES = [
        ('Главврач', 'Главврач'),
        ('Врач', 'Врач'),
        ('Медсестра', 'Медсестра'),
        ('Медбрат', 'Медбрат'),
    ]


    SPECIALISATION_CHOICES = [
        ("Терапевт", "Терапевт"),
        ("Хирург", "Хирург"),
        ("Педиатр", "Педиатр"),
        ("Офтальмолог", "Офтальмолог"),
        ("Отоларинголог", "Отоларинголог"),
        ("Невролог", "Невролог"),
        ("Анестезиолог", "Анестезиолог"),
        ("Физиотерапевт", "Физиотерапевт"),
        ("Дерматолог", "Дерматолог"),
        ("Инфекционист", "Инфекционист"),
        ("Реаниматолог", "Реаниматолог"),
    ]

    medical_staff_name = forms.CharField(label='ФИО')
    medical_staff_gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Пол')
    medical_staff_birthday = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    medical_staff_post = forms.ChoiceField(
        choices=POST_CHOICES,
        label='Должность'
    )

    medical_staff_specialisation = forms.ChoiceField(
        label="Специализация",
        choices=SPECIALISATION_CHOICES
    )

    class Meta:
        model = MedicalStaff
        fields = [
            'medical_staff_name',
            'medical_staff_birthday',
            'medical_staff_gender',
            'medical_staff_post',
            'medical_staff_specialisation',
        ]

class ProceduresExecutionForm(forms.ModelForm):
    class Meta:
        model = ProceduresExecution
        fields = ['procedures_id', 'procedures_execution_date', 'procedures_execution_duration', 'procedures_execution_comment', 'procedures_execution_status']

class MedicationDispensingForm(forms.ModelForm):
    class Meta:
        model = MedicationDispensing
        fields = ['medication_id', 'medication_dispensing_dose', 'medication_dispensing_comment', 'medication_dispensing_status']
        widgets = {
            'medication_dispensing_date': forms.DateInput(attrs={'type': 'date', 'value': date.today()})
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = MedicalStaff
        fields = ['medical_staff_name', 'medical_staff_birthday', 'medical_staff_gender', 'medical_staff_post', 'medical_staff_specialisation']

class AddProcedureExecutionForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('В ожидании', 'В ожидании'),
        ('Выполнено', 'Выполнено'),
        ('Отменено', 'Отменено'),
    ]

    procedures_execution_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Статус",
        widget=forms.Select,
        initial='В ожидании'  
    )

    class Meta:
        model = ProceduresExecution
        fields = ['procedures_id', 'procedures_execution_duration', 'procedures_execution_comment', 'procedures_execution_status']
        widgets = {
            'procedures_execution_date': forms.DateInput(attrs={'type': 'date', 'value': date.today()})
        }

class MedicationDispensingForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('В ожидании', 'В ожидании'),
        ('Выполнено', 'Выполнено'),
        ('Отменено', 'Отменено'),
    ]
    
    medication_dispensing_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Статус",
        widget=forms.Select,
        initial='В ожидании'  
    )

    class Meta:
        model = MedicationDispensing
        fields = ['medication_id', 'medication_dispensing_dose', 'medication_dispensing_comment', 'medication_dispensing_status']
        widgets = {
            'medication_dispensing_date': forms.DateInput(attrs={'type': 'date', 'value': date.today()})
        }