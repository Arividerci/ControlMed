from .models import Patient, MedicalStaff, MedicalBook, Hospitalization, Purpose, Medication, Procedures, IncludesReception, IncludesConducting, MedicalBookContent
from .forms import RegisterStep1Form, RegisterStep2Form, LoginForm, AddPatientForm,  HospitalizationForm, PurposeForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,  get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse
from datetime import date, timedelta
from django.views.decorators.http import require_POST

import os
import json
import traceback

def home(request):
    return render(request, 'main/home.html')

@login_required
def cabinet(request):
    return render(request, 'main/cabinet.html')

@login_required
def appointments(request):
    return render(request, 'main/appointments.html')

@login_required
def patients(request):
    all_patients = Patient.objects.all()
    return render(request, 'main/patients.html', {'patients': all_patients})


@login_required
def appointments_view(request):
    staff = MedicalStaff.objects.get(user=request.user)

    appointments = Purpose.objects.filter(
        hospitalization__medical_staff=staff,
        purpose_status__in=['Активный', 'Приостановлен']
    ).select_related('hospitalization', 'hospitalization__patient')

    return render(request, 'main/appointments_list.html', {
        'appointments': appointments
    })

@login_required
def add_patient(request):
    if request.method == 'POST':
        form = AddPatientForm(request.POST, request.FILES) 
        if form.is_valid():
            patient = form.save()
            MedicalBook.objects.create(patient=patient)
            return redirect('patients')
    else:
        form = AddPatientForm()
    return render(request, 'main/add_patient.html', {'form': form})

@csrf_exempt
def delete_patient(request, patient_id):
    if request.method == 'POST':
        try:
            patient = get_object_or_404(Patient, pk=patient_id)
            patient.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})



@csrf_exempt
def delete_selected_patients(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            if not isinstance(ids, list):
                return JsonResponse({'success': False, 'error': 'Invalid ID list'}, status=400)

            # Удаление пациентов
            Patient.objects.filter(patient_id__in=ids).delete()

            return JsonResponse({'success': True})
        except Exception as e:
            # Вывод ошибки в консоль контейнера
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def remove_patient_photo(request, patient_id):
    if request.method == 'POST':
        try:
            patient = get_object_or_404(Patient, pk=patient_id)
            if patient.patient_photo:
                patient.patient_photo.delete(save=False)  # удалить физически
                patient.patient_photo = 'no-photo.webp'  # путь к фото по умолчанию
                patient.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
def register_step1(request):

    if not request.user.is_authenticated:
        return redirect('login')

    try:
        staff = MedicalStaff.objects.get(user=request.user)
        if staff.medical_staff_post != 'Главврач':
            return HttpResponseForbidden("Доступ запрещён. Только главврач может регистрировать пользователей.")
    except MedicalStaff.DoesNotExist:
        return HttpResponseForbidden("Доступ запрещён. Только медперсонал может регистрировать пользователей.")
    
    if request.method == 'POST':
        form = RegisterStep1Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            request.session['reg_login'] = username
            request.session['reg_email'] = email
            request.session['reg_password'] = password

            return redirect('register_step2')
    else:
        form = RegisterStep1Form()
    return render(request, 'main/register_step1.html', {'form': form})

@login_required
def register_step2(request):
    if request.method == 'POST':
        form = RegisterStep2Form(request.POST)
        if form.is_valid():
            login_value = request.session.get('reg_login')
            email = request.session.get('reg_email')  
            password = request.session.get('reg_password')

            if not (login_value and email and password):
                return redirect('register_step1')

            user, created = User.objects.get_or_create(username=login_value)
            if created:
                user.set_password(password)
                user.email = email 

                full_name = form.cleaned_data['medical_staff_name'].strip()
                name_parts = full_name.split()

                if len(name_parts) >= 2:
                    user.last_name = name_parts[0]              
                    user.first_name = name_parts[1]             
                if len(name_parts) == 3:
                    user.first_name += f" {name_parts[2]}"

                user.save()

            if not MedicalStaff.objects.filter(medical_staff_name=form.cleaned_data['medical_staff_name']).exists():
                MedicalStaff.objects.create(
                    user=user,
                    medical_staff_name=form.cleaned_data['medical_staff_name'],
                    medical_staff_birthday=form.cleaned_data['medical_staff_birthday'],
                    medical_staff_gender=form.cleaned_data['medical_staff_gender'],
                    medical_staff_post=form.cleaned_data['medical_staff_post'],
                    medical_staff_specialisation=form.cleaned_data['medical_staff_specialisation'],
                )

            login(request, user)
            request.session.pop('reg_login', None)
            request.session.pop('reg_password', None)
            request.session.pop('reg_email', None)  

            return redirect('cabinet')
        else:
            print('Ошибки валидации формы:', form.errors)
    else:
        form = RegisterStep2Form()

    return render(request, 'main/register_step2.html', {'form': form})

@login_required
def cabinet(request):
    try:
        staff = MedicalStaff.objects.get(user=request.user)
    except MedicalStaff.DoesNotExist:
        staff = None
    return render(request, 'main/cabinet.html', {'staff': staff})

@login_required
def patients(request):
    all_patients = Patient.objects.all()
    return render(request, 'main/patients.html', {'patients': all_patients})


def login_view(request):
    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('cabinet')  # перенаправим в личный кабинет
            else:
                error_message = "Неверный логин или пароль"
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {'form': form, 'error_message': error_message})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
import datetime
from .models import Patient, Hospitalization, Purpose
from .forms import HospitalizationForm, PurposeForm


@login_required
def patient_detail(request, patient_id):
    today = datetime.date.today()
    patient = get_object_or_404(Patient, pk=patient_id)
    active_tab = request.GET.get('tab', 'main')
    medical_book = MedicalBook.objects.filter(patient=patient).first()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'patient':
            patient.patient_name = ' '.join([
                request.POST.get('last_name', ''),
                request.POST.get('first_name', ''),
                request.POST.get('patronymic', '')
            ])
            patient.patient_birthday = request.POST.get('birthday')
            patient.patient_gender = request.POST.get('gender')
            patient.patient_height = request.POST.get('height')
            patient.patient_weight = request.POST.get('weight')
            patient.patient_blood_type = request.POST.get('blood_type')

            if 'photo' in request.FILES:
                patient.patient_photo = request.FILES['photo']

            patient.save()
            return redirect('patient_detail', patient_id=patient_id)

        elif form_type == 'hospitalization':
            form = HospitalizationForm(request.POST)
            if form.is_valid():
                try:
                    staff = MedicalStaff.objects.get(user=request.user)
                except MedicalStaff.DoesNotExist:
                    messages.error(request, "Вы не привязаны к медперсоналу.")
                    return redirect('patient_detail', patient_id=patient_id)

                # Проверяем: есть ли уже госпитализация
                hospitalization = Hospitalization.objects.filter(
                    patient=patient
                ).order_by('-hospitalization_startdate').first()

                if hospitalization:
                    # Обновляем существующую запись
                    hospitalization.hospitalization_room = form.cleaned_data['hospitalization_room']
                    hospitalization.hospitalization_startdate = form.cleaned_data['hospitalization_startdate']
                    hospitalization.hospitalization_enddate = form.cleaned_data['hospitalization_enddate']
                    hospitalization.medical_staff = staff
                    hospitalization.save()
                else:
                    # Создаём новую
                    new_hosp = form.save(commit=False)
                    new_hosp.patient = patient
                    new_hosp.medical_staff = staff
                    new_hosp.save()

                return redirect(f'/patients/{patient_id}/?tab=hospitalization')
            else:
                print("Форма госпитализации невалидна:", form.errors)
                messages.error(request, f"Ошибка формы госпитализации: {form.errors}")



        elif form_type == 'purpose':
            form = PurposeForm(request.POST)
            if form.is_valid():
                purp = form.save(commit=False)
                purp.patient = patient

                try:
                    purp.medical_staff = MedicalStaff.objects.get(user=request.user)
                except MedicalStaff.DoesNotExist:
                    messages.error(request, "Вы не привязаны к медперсоналу.")
                    return redirect(f'/patients/{patient_id}/?tab=purpose')

                hospitalization_id = request.POST.get('hospitalization')
                try:
                    purp.hospitalization = Hospitalization.objects.get(pk=hospitalization_id)
                except Hospitalization.DoesNotExist:
                    messages.error(request, "Госпитализация не найдена.")
                    return redirect(f'/patients/{patient_id}/?tab=purpose')

                purp.save()
                return redirect(f'/patients/{patient_id}/?tab=purpose')

    today = datetime.date.today()
    hospitalization = Hospitalization.objects.filter(
        patient_id=patient_id,
        hospitalization_startdate__lte=today,
        hospitalization_enddate__gte=today
    ).first()

    return render(request, 'main/patient_detail.html', {
    'patient': patient,
    'hospitalization': hospitalization,
    'medical_book': medical_book,
    'form': HospitalizationForm(),
    'purpose_form': PurposeForm(),
    'active_tab': active_tab,
    'hospitalizations': Hospitalization.objects.filter(patient=patient),
    'medical_staff': MedicalStaff.objects.all(),
    
})
@login_required
def patient_hospitalization(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    hospitalization = Hospitalization.objects.filter(
        patient=patient,
        hospitalization_startdate__lte=datetime.date.today(),
        hospitalization_enddate__gte=datetime.date.today()
    ).first()

    if request.method == 'POST':
        form = HospitalizationForm(request.POST, instance=hospitalization)
        if form.is_valid():
            hosp = form.save(commit=False)
            hosp.patient = patient
            hosp.medical_staff = MedicalStaff.objects.get(user=request.user)
            hosp.save()
            return redirect('patient_hospitalization', patient_id=patient_id)
    else:
        form = HospitalizationForm(instance=hospitalization)

    return render(request, 'main/patient_hospitalization.html', {
        'patient': patient,
        'form': form,
        'hospitalization': hospitalization,
        'active_page': 'hospitalization'
    })

@login_required
def patient_purpose(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    purposes = Purpose.objects.filter(hospitalization__patient=patient)
    medications = Medication.objects.all()
    procedures = Procedures.objects.all()

    # Найдём активную госпитализацию
    hospitalization = Hospitalization.objects.filter(
        patient=patient,
        hospitalization_startdate__lte=date.today(),
        hospitalization_enddate__gte=date.today()
    ).first()

    # Медперсонал
    try:
        medical_staff = MedicalStaff.objects.get(user=request.user)
    except MedicalStaff.DoesNotExist:
        medical_staff = None

    # Обработка POST (если создаётся новое назначение)
    if request.method == 'POST':
        form = PurposeForm(request.POST)
        if form.is_valid():
            purpose = form.save(commit=False)
            purpose.medical_staff = medical_staff
            purpose.hospitalization = hospitalization
            purpose.purpose_status = (
                "Активный" if purpose.purpose_startdate + timedelta(days=purpose.purpose_duration) >= date.today()
                else "Завершено"
            )
            purpose.save()
            return redirect('patient_purpose', patient_id=patient_id)
    else:
        form = PurposeForm(initial={'purpose_startdate': date.today()})

    # --- Словари выбора медикаментов/процедур для каждого назначения ---
    medications_selected = {
        p.purpose_id: list(
            IncludesReception.objects.filter(purpose=p).values_list("medication_id", flat=True)
        )
        for p in purposes
    }
    procedures_selected = {
        p.purpose_id: list(
            IncludesConducting.objects.filter(purpose=p).values_list("procedures_id", flat=True)
        )
        for p in purposes
    }

    return render(request, 'main/patient_purpose.html', {
        'patient': patient,
        'form': form,
        'purposes': purposes,
        'medications': medications,
        'procedures': procedures,
        'medications_selected': medications_selected,
        'procedures_selected': procedures_selected,
        'active_page': 'purpose',
    })

@csrf_exempt
@login_required
def delete_purpose_row(request, patient_id, purpose_id):
    if request.method == 'POST':
        try:
            purpose = get_object_or_404(Purpose, pk=purpose_id)
            IncludesReception.objects.filter(purpose=purpose).delete()
            IncludesConducting.objects.filter(purpose=purpose).delete()
            purpose.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def save_purpose_row(request, patient_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            purpose_id = data.get('id')

            # Получаем медперсонал
            medical_staff = MedicalStaff.objects.get(user=request.user)

            # Получаем активную госпитализацию
            hospitalization = Hospitalization.objects.filter(
                patient_id=patient_id,
                hospitalization_startdate__lte=date.today(),
                hospitalization_enddate__gte=date.today()
            ).first()

            if not hospitalization:
                return JsonResponse({'success': False, 'error': 'Нет активной госпитализации'})

            # Рассчитываем статус автоматически
            start_date = date.fromisoformat(data['startdate'])
            duration = int(data['duration'])
            calculated_status = "Активный" if start_date + timedelta(days=duration) >= date.today() else "Завершено"
            status = data.get('status') or calculated_status

            # Обновление или создание назначения
            if purpose_id:
                purpose = Purpose.objects.get(pk=purpose_id)
                purpose.purpose_startdate = start_date
                purpose.purpose_duration = duration
                purpose.purpose_diagnosis = data['diagnosis']
                purpose.purpose_status = status
                purpose.medical_staff = medical_staff
                purpose.hospitalization = hospitalization
                purpose.save()

                # Удаляем старые связи
                IncludesReception.objects.filter(purpose=purpose).delete()
                IncludesConducting.objects.filter(purpose=purpose).delete()
            else:
                purpose = Purpose.objects.create(
                    purpose_startdate=start_date,
                    purpose_duration=duration,
                    purpose_diagnosis=data['diagnosis'],
                    purpose_status=status,
                    medical_staff=medical_staff,
                    hospitalization=hospitalization
                )

            # Добавляем медикаменты
            IncludesReception.objects.bulk_create([
                IncludesReception(medication_id=med_id, purpose=purpose)
                for med_id in data.get('medications', [])
            ])

            # Добавляем процедуры
            IncludesConducting.objects.bulk_create([
                IncludesConducting(procedures_id=proc_id, purpose=purpose)
                for proc_id in data.get('procedures', [])
            ])

            return JsonResponse({"success": True, "id": purpose.purpose_id})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})

def patient_medbook(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    medicalbook = MedicalBook.objects.get(patient=patient)

    # Получаем записи MedicalBookContent с необходимыми связями
    contents_qs = MedicalBookContent.objects.filter(medicalbook_id=medicalbook.medicalbook_id).select_related('purpose')

    medbook_content = []
    for entry in contents_qs:
        # Получаем препараты для назначения
        medications_qs = IncludesReception.objects.filter(purpose=entry.purpose).select_related('medication')
        medications = [med.medication.medication_name for med in medications_qs]

        # Получаем процедуры для назначения
        procedures_qs = IncludesConducting.objects.filter(purpose=entry.purpose).select_related('procedures')
        procedures = [proc.procedures.procedures_name for proc in procedures_qs]

        medbook_content.append({
            'medical_book_content_id': entry.medical_book_content_id,
            'medical_book_content_notes': entry.medical_book_content_notes,
            'purpose': entry.purpose,
            'medications': medications,
            'procedures': procedures,
            'doctor': entry.purpose.medical_staff.medical_staff_name if entry.purpose.medical_staff else "Неизвестен",
        })

    return render(request, 'main/patient_medbook.html', {
        'patient': patient,
        'medicalbook': medicalbook,
        'medbook_content': medbook_content,
    })

@require_POST
def update_medical_book_comment(request, patient_id, content_id):
    comment = request.POST.get('comment', '').strip()
    content = get_object_or_404(MedicalBookContent, pk=content_id)

    content.medical_book_content_notes = comment
    content.save()

    return redirect('patient_medbook', patient_id=patient_id)


@login_required
def procedures_view(request):
    # Логика для страницы процедур
    return render(request, 'main/procedures.html')

@login_required
def medications_view(request):
    # Пока можно просто вернуть пустой шаблон или добавить свою логику
    return render(request, 'main/medications.html')