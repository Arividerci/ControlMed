from .models import Patient, MedicalStaff, MedicalBook, Hospitalization, Purpose, Medication, Procedures, IncludesReception, IncludesConducting, MedicalBookContent, ProceduresExecution, MedicationDispensing
from .forms import RegisterStep1Form, RegisterStep2Form, LoginForm, AddPatientForm,  HospitalizationForm, PurposeForm, ProceduresExecutionForm, EditProfileForm, AddProcedureExecutionForm, MedicationDispensingForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,  get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from datetime import date, timedelta
from django.views.decorators.http import require_POST
from django.db.models import Count, Q,  F, ExpressionWrapper, DateField
from django.db import transaction
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics


import os
import json
import traceback


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('cabinet') 
    else:
        return redirect('login')
    
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
def generate_report(request):
    staff = MedicalStaff.objects.get(user=request.user)
    
    if staff.medical_staff_post != 'Главврач':
        return HttpResponseForbidden("Доступ запрещен. Только главврач может создавать отчеты.")

    assignments = Purpose.objects.all().select_related('hospitalization', 'hospitalization__patient', 'medical_staff')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="assignments_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    font_path = os.path.join('static', 'fonts', 'Arial.ttf')
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        p.setFont('Arial', 12)
    else:
        p.setFont("Helvetica", 12)

    p.setFont("Arial", 16)
    p.drawString(100, height - 50, "Отчет по заданиям")

    y_position = height - 80
    for assignment in assignments:
        patient_name = assignment.hospitalization.patient.patient_name
        diagnosis = assignment.purpose_diagnosis
        start_date = assignment.purpose_startdate
        duration = assignment.purpose_duration
        status = assignment.purpose_status
        medical_staff = assignment.medical_staff  
        doctor_name = medical_staff.medical_staff_name if medical_staff else "Неизвестен"
        doctor_post = medical_staff.medical_staff_post if medical_staff else "Неизвестен"

        p.setFont("Arial", 10)
        p.drawString(50, y_position, f"Пациент: {patient_name}")
        y_position -= 15
        p.drawString(50, y_position, f"Диагноз: {diagnosis}")
        y_position -= 15
        p.drawString(50, y_position, f"Дата лечения: {start_date}")
        y_position -= 15
        p.drawString(50, y_position, f"Продолжительность: {duration} дней")
        y_position -= 15
        p.drawString(50, y_position, f"Статус: {status}")
        y_position -= 15
        p.drawString(50, y_position, f"Назначение выполнял(а): {doctor_post} {doctor_name}")
        y_position -= 20  

        if y_position < 100:
            p.showPage()
            y_position = height - 100

    p.showPage()
    p.save()

    return response
@login_required
def generate_selected_patients_report(request):
    if request.method == 'POST':
        patient_ids = json.loads(request.body).get('ids', [])
        patients = Patient.objects.filter(id__in=patient_ids)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="patients_report.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        p.setFont("Helvetica", 12)
        p.drawString(100, height - 50, "Отчет по выбранным пациентам")

        y_position = height - 80
        for patient in patients:
            p.drawString(50, y_position, f"ФИО: {patient.patient_name}")
            y_position -= 15
            p.drawString(50, y_position, f"Дата рождения: {patient.patient_birthday}")
            y_position -= 15
            p.drawString(50, y_position, f"Пол: {patient.patient_gender}")
            y_position -= 15
            p.drawString(50, y_position, f"Рост: {patient.patient_height} см")
            y_position -= 15
            p.drawString(50, y_position, f"Вес: {patient.patient_weight} кг")
            y_position -= 20

            if y_position < 100:
                p.showPage()
                y_position = height - 100

        p.showPage()
        p.save()

        return response
    
@login_required
def generate_hospitalization_report(request):
    staff = MedicalStaff.objects.get(user=request.user)
    
    if staff.medical_staff_post != 'Главврач':
        return HttpResponseForbidden("Доступ запрещен. Только главврач может создавать отчеты.")

    hospitalizations = Hospitalization.objects.all().select_related('patient', 'medical_staff')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="hospitalization_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    font_path = os.path.join('static', 'fonts', 'Arial.ttf')
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        p.setFont('Arial', 12)
    else:
        p.setFont("Helvetica", 12)

    p.setFont("Arial", 16)
    p.drawString(100, height - 50, "Отчет по госпитализациям")

    y_position = height - 80
    for hospitalization in hospitalizations:
        patient_name = hospitalization.patient.patient_name
        start_date = hospitalization.hospitalization_startdate
        end_date = hospitalization.hospitalization_enddate
        room = hospitalization.hospitalization_room
        medical_staff = hospitalization.medical_staff  
        staff_name = medical_staff.medical_staff_name if medical_staff else "Неизвестен"
        staff_post = medical_staff.medical_staff_post if medical_staff else "Неизвестен"

        p.setFont("Arial", 10)
        p.drawString(50, y_position, f"Пациент: {patient_name}")
        y_position -= 15
        p.drawString(50, y_position, f"Дата начала: {start_date}")
        y_position -= 15
        p.drawString(50, y_position, f"Дата окончания: {end_date}")
        y_position -= 15
        p.drawString(50, y_position, f"Палата: {room}")
        y_position -= 15
        p.drawString(50, y_position, f"Госпитализацию провел(а) ФИО: {staff_post} {staff_name}")
        y_position -= 20 
        
        if y_position < 100:
            p.showPage()
            y_position = height - 100

    # Завершаем создание PDF
    p.showPage()
    p.save()

    return response
@login_required
def assignments_view(request):
    staff = MedicalStaff.objects.get(user=request.user)

    assignments = Purpose.objects.filter(
        purpose_status__in=['Активный', 'Приостановлен'] if staff.medical_staff_post != 'Главврач' else ['Активный', 'Приостановлен', 'Завершено'],
        hospitalization__medical_staff=staff
    ).select_related('hospitalization', 'hospitalization__patient')

    print(f"Найдено назначений: {assignments.count()}")

    if staff.medical_staff_post == 'Главврач':
        for assignment in assignments:
            assignment.medications = IncludesReception.objects.filter(purpose=assignment).select_related('medication')
            assignment.procedures = IncludesConducting.objects.filter(purpose=assignment).select_related('procedures')

            print(f"Назначение {assignment.purpose_id} имеет {assignment.medications.count()} медикаментов и {assignment.procedures.count()} процедур")

    return render(request, 'main/assignments.html', {
        'assignments': assignments,
        'staff': staff,
    })


# Представление для редактирования профиля
@login_required
def edit_profile(request):
    staff = MedicalStaff.objects.get(user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация успешно обновлена.')
            return redirect('cabinet')  # Перенаправление в кабинет после успешного сохранения
    else:
        form = EditProfileForm(instance=staff)

    return render(request, 'main/edit_profile.html', {'form': form})


@login_required
def delete_medical_staff(request):
    staff = MedicalStaff.objects.get(user=request.user)  

    if request.method == 'POST':
        Purpose.objects.filter(medical_staff=staff).delete()
        MedicalBookContent.objects.filter(purpose__medical_staff=staff).delete()
        IncludesReception.objects.filter(purpose__medical_staff=staff).delete()
        IncludesConducting.objects.filter(purpose__medical_staff=staff).delete()

        staff.delete()  
        messages.success(request, 'Ваш аккаунт был успешно удален.')
        return redirect('login')  

    return redirect('cabinet') 

@login_required
def delete_account(request):
    staff = MedicalStaff.objects.get(user=request.user)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Аккаунт успешно удален.')
        return redirect('login')  # После удаления перенаправить на страницу логина

    return render(request, 'main/delete_account.html')

@login_required
def add_hospitalization(request, patient_id):
    patient = Patient.objects.get(pk=patient_id)

    # Ищем медсестру с наименьшим количеством госпитализаций
    nurse = MedicalStaff.objects.filter(medical_staff_post="Медсестра").annotate(num_hospitals=Count('hospitalization')).order_by('num_hospitals').first()

    if request.method == 'POST':
        start_date = request.POST['hospitalization_startdate']
        end_date = request.POST['hospitalization_enddate']
        room = request.POST['hospitalization_room']
        
        # Создаем госпитализацию и назначаем медсестру
        hospitalization = Hospitalization.objects.create(
            hospitalization_startdate=start_date,
            hospitalization_enddate=end_date,
            hospitalization_room=room,
            medical_staff=nurse,  # Закрепляем медсестру с наименьшим количеством госпитализаций
            patient=patient
        )

        return redirect('patient_detail', patient_id=patient.id)

    return render(request, 'main/add_hospitalization.html', {'patient': patient})

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

def cabinet(request):
    staff = MedicalStaff.objects.get(user=request.user)  
    staff_data = {
        'medical_staff_name': staff.medical_staff_name,
        'medical_staff_post': staff.medical_staff_post,
        'medical_staff_specialisation': staff.medical_staff_specialisation,
        'medical_staff_birthday': staff.medical_staff_birthday,
    }

    return render(request, 'main/cabinet.html', {'staff': staff_data})

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
                return redirect('cabinet')  
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

                hospitalization = Hospitalization.objects.filter(
                    patient=patient
                ).order_by('-hospitalization_startdate').first()

                if hospitalization:
                    hospitalization.hospitalization_room = form.cleaned_data['hospitalization_room']
                    hospitalization.hospitalization_startdate = form.cleaned_data['hospitalization_startdate']
                    hospitalization.hospitalization_enddate = form.cleaned_data['hospitalization_enddate']
                    hospitalization.medical_staff = staff
                    hospitalization.save()
                else:
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

    purposes_for_doctor = purposes.exclude(medical_staff__medical_staff_post__in=['Медсестра', 'Медбрат'])
    medications = Medication.objects.all()
    procedures = Procedures.objects.all()

    hospitalization = Hospitalization.objects.filter(
        patient=patient,
        hospitalization_startdate__lte=date.today(),
        hospitalization_enddate__gte=date.today()
    ).first()

    try:
        medical_staff = MedicalStaff.objects.get(user=request.user)
    except MedicalStaff.DoesNotExist:
        medical_staff = None

    if request.method == 'POST':
        form = PurposeForm(request.POST)
        if form.is_valid():
            purpose = form.save(commit=False)
            purpose.medical_staff = medical_staff
            purpose.hospitalization = hospitalization
            purpose.purpose_status = "Активный" if purpose.purpose_startdate + timedelta(days=purpose.purpose_duration) >= date.today() else "Завершено"
            purpose.save()
            return redirect('patient_purpose', patient_id=patient_id)
    else:
        form = PurposeForm(initial={'purpose_startdate': date.today()})

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
        'purposes': purposes_for_doctor,  
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
            # Получаем назначение для врача
            purpose = get_object_or_404(Purpose, pk=purpose_id)
            
            # Удаляем все связанные медикаменты и процедуры для назначения
            IncludesReception.objects.filter(purpose=purpose).delete()
            IncludesConducting.objects.filter(purpose=purpose).delete()

            # Найдем назначение для медсестры/медбрата с тем же госпитализацией и датой
            nurse_purpose = Purpose.objects.filter(
                hospitalization=purpose.hospitalization,
                purpose_startdate=purpose.purpose_startdate,
            ).exclude(purpose_id=purpose.purpose_id).filter(
                Q(medical_staff__medical_staff_post='Медсестра') | Q(medical_staff__medical_staff_post='Медбрат')
            ).first()

            # Если назначение для медсестры/медбрата найдено, удаляем его
            if nurse_purpose:
                IncludesReception.objects.filter(purpose=nurse_purpose).delete()
                IncludesConducting.objects.filter(purpose=nurse_purpose).delete()
                nurse_purpose.delete()

            # Удаляем назначение для врача
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
            medical_staff = MedicalStaff.objects.get(user=request.user)

            # Получаем пациента
            patient = get_object_or_404(Patient, pk=patient_id)

            hospitalization = Hospitalization.objects.filter(
                patient_id=patient_id,
                hospitalization_startdate__lte=date.today(),
                hospitalization_enddate__gte=date.today()
            ).first()

            if not hospitalization:
                return JsonResponse({'success': False, 'error': 'Нет активной госпитализации'})

            start_date = date.fromisoformat(data['startdate'])
            duration = int(data['duration'])
            calculated_status = "Активный" if start_date + timedelta(days=duration) >= date.today() else "Завершено"
            status = data.get('status') or calculated_status

            with transaction.atomic():
                if purpose_id:
                    purpose = Purpose.objects.get(pk=purpose_id)
                    purpose.purpose_startdate = start_date
                    purpose.purpose_duration = duration
                    purpose.purpose_diagnosis = data['diagnosis']
                    purpose.purpose_status = status
                    purpose.medical_staff = medical_staff
                    purpose.hospitalization = hospitalization
                    purpose.save()

                    # Находим назначение медсестры/медбрата с таким же hospitalization и датой
                    nurse_purpose = Purpose.objects.filter(
                        hospitalization=hospitalization,
                        purpose_startdate=purpose.purpose_startdate,
                    ).exclude(purpose_id=purpose.purpose_id).filter(
                        Q(medical_staff__medical_staff_post='Медсестра') | Q(medical_staff__medical_staff_post='Медбрат')
                    ).first()

                    if nurse_purpose:
                        # Обновляем назначение медсестры
                        nurse_purpose.purpose_startdate = start_date
                        nurse_purpose.purpose_duration = duration
                        nurse_purpose.purpose_diagnosis = data['diagnosis']
                        nurse_purpose.purpose_status = status
                        nurse_purpose.hospitalization = hospitalization
                        nurse_purpose.save()

                    # Удаляем старые связи
                    IncludesReception.objects.filter(Q(purpose=purpose) | Q(purpose=nurse_purpose)).delete()
                    IncludesConducting.objects.filter(Q(purpose=purpose) | Q(purpose=nurse_purpose)).delete()

                    # Создаем новые связи для врача
                    IncludesReception.objects.bulk_create([ 
                        IncludesReception(medication_id=med_id, purpose=purpose)
                        for med_id in data.get('medications', [])
                    ])
                    IncludesConducting.objects.bulk_create([
                        IncludesConducting(procedures_id=proc_id, purpose=purpose)
                        for proc_id in data.get('procedures', [])
                    ])

                    # Создаём новые связи для медсестры
                    if nurse_purpose:
                        IncludesReception.objects.bulk_create([ 
                            IncludesReception(medication_id=med_id, purpose=nurse_purpose)
                            for med_id in data.get('medications', [])
                        ])
                        IncludesConducting.objects.bulk_create([
                            IncludesConducting(procedures_id=proc_id, purpose=nurse_purpose)
                            for proc_id in data.get('procedures', [])
                        ])

                    # Добавляем запись в медицинскую книгу для врача
                    medical_book = MedicalBook.objects.get(patient=patient)
                    if not MedicalBookContent.objects.filter(purpose=purpose).exists():
                        medical_book_content = MedicalBookContent.objects.create(
                            medicalbook=medical_book,
                            purpose=purpose,
                            medical_book_content_notes=f"Назначение: {purpose.purpose_diagnosis}; Начало: {purpose.purpose_startdate}; Длительность: {purpose.purpose_duration} дней; Статус: {purpose.purpose_status}"
                        )
                        print("Запись в медицинскую книгу добавлена для врача!")

                else:
                    purpose = Purpose.objects.create(
                        purpose_startdate=start_date,
                        purpose_duration=duration,
                        purpose_diagnosis=data['diagnosis'],
                        purpose_status=status,
                        medical_staff=medical_staff,
                        hospitalization=hospitalization
                    )

                    # Назначаем медсестру с минимальной нагрузкой
                    nurse = MedicalStaff.objects.filter(medical_staff_post='Медсестра').annotate(
                        num_purposes=Count('purpose')
                    ).order_by('num_purposes').first()

                    nurse_purpose = None
                    if nurse:
                        nurse_purpose = Purpose.objects.create(
                            purpose_startdate=start_date,
                            purpose_duration=duration,
                            purpose_diagnosis=data['diagnosis'],
                            purpose_status=status,
                            medical_staff=nurse,
                            hospitalization=hospitalization
                        )

                    # Создаем связи для врача
                    IncludesReception.objects.bulk_create([ 
                        IncludesReception(medication_id=med_id, purpose=purpose)
                        for med_id in data.get('medications', [])
                    ])
                    IncludesConducting.objects.bulk_create([
                        IncludesConducting(procedures_id=proc_id, purpose=purpose)
                        for proc_id in data.get('procedures', [])
                    ])

                    # Создаем связи для медсестры
                    if nurse_purpose:
                        IncludesReception.objects.bulk_create([ 
                            IncludesReception(medication_id=med_id, purpose=nurse_purpose)
                            for med_id in data.get('medications', [])
                        ])
                        IncludesConducting.objects.bulk_create([
                            IncludesConducting(procedures_id=proc_id, purpose=nurse_purpose)
                            for proc_id in data.get('procedures', [])
                        ])

                        medical_book = MedicalBook.objects.get(patient=patient)

                        # Убедимся, что не дублируем записи
                        if not MedicalBookContent.objects.filter(purpose=purpose).exists():
                            medical_book_content = MedicalBookContent.objects.create(
                                medicalbook_id=medical_book.medicalbook_id, 
                                purpose=purpose,
                                medical_book_content_notes=f"Назначение: {purpose.purpose_diagnosis}; Начало: {purpose.purpose_startdate}; Длительность: {purpose.purpose_duration} дней; Статус: {purpose.purpose_status}"
                            )
                            print("Запись в медицинскую книгу добавлена для врача!")


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

@login_required
def update_medical_staff(request):
    staff = MedicalStaff.objects.get(user=request.user)
    
    if request.method == 'POST':
        staff.medical_staff_name = request.POST['staff_name']
        staff.medical_staff_post = request.POST['staff_post']
        staff.medical_staff_specialisation = request.POST['staff_specialisation']
        staff.medical_staff_birthday = request.POST['staff_birthday']
        staff.save()

        messages.success(request, 'Данные успешно обновлены!')
        return redirect('cabinet')

    return render(request, 'main/cabinet.html', {'staff': staff})

@require_POST
def update_medical_book_comment(request, patient_id, content_id):
    comment = request.POST.get('comment', '').strip()
    content = get_object_or_404(MedicalBookContent, pk=content_id)

    content.medical_book_content_notes = comment
    content.save()

    return redirect('patient_medbook', patient_id=patient_id)

@login_required
def assignments_view(request):
    staff = MedicalStaff.objects.get(user=request.user)  # Получаем текущего медицинского сотрудника
    today = date.today()  # Получаем сегодняшнюю дату

    # Инициализация переменной assignments
    assignments = []

    # Получаем назначения только для сотрудников (не для главврача), у которых дата начала <= сегодняшняя дата <= дата окончания
    if staff.medical_staff_post != 'Главврач':
        assignments = Purpose.objects.filter(
            purpose_status__in=['Активный', 'Приостановлен'],  # Только активные и приостановленные назначения
            hospitalization__medical_staff=staff,  # Привязка к медицинскому сотруднику
            purpose_startdate__lte=today,  # Начало назначения раньше или равно сегодняшней дате
        ).select_related('hospitalization', 'hospitalization__patient').distinct('hospitalization')

        # Загружаем медикаменты и процедуры для каждого назначения
        for assignment in assignments:
            # Вычисляем конечную дату назначения
            end_date = assignment.purpose_startdate + timedelta(days=assignment.purpose_duration)

            # Проверяем, попадает ли сегодняшняя дата в промежуток от начала до конца
            if assignment.purpose_startdate <= today <= end_date:
                # Получаем медикаменты для назначения
                assignment.medications = Medication.objects.filter(
                    medication_id__in=IncludesReception.objects.filter(purpose_id=assignment.purpose_id).values('medication_id')
                )

                # Получаем процедуры для назначения
                assignment.procedures = Procedures.objects.filter(
                    procedures_id__in=IncludesConducting.objects.filter(purpose_id=assignment.purpose_id).values('procedures_id')
                )

                # Получаем врача и помощника для каждого назначения
                assignment.doctor = MedicalStaff.objects.get(medical_staff_id=assignment.medical_staff_id)

                # Получаем медсестру или медбрата как помощника
                assignment.assistant = MedicalStaff.objects.filter(
                    medical_staff_post__in=['Медсестра', 'Медбрат'],
                    user=assignment.medical_staff.user
                ).first()

    # Для главврача загружаем все назначения, но с фильтрацией по дате начала и окончания
    if staff.medical_staff_post == 'Главврач':
        assignments = Purpose.objects.filter(
            purpose_status__in=['Активный', 'Приостановлен', 'Завершено'],
            purpose_startdate__lte=today,  # Начало назначения раньше или равно сегодняшней дате
        ).select_related('hospitalization', 'hospitalization__patient')

        # Загружаем медикаменты и процедуры для каждого назначения
        for assignment in assignments:
            # Вычисляем конечную дату назначения
            end_date = assignment.purpose_startdate + timedelta(days=assignment.purpose_duration)

            # Проверяем, попадает ли сегодняшняя дата в промежуток от начала до конца
            if assignment.purpose_startdate <= today <= end_date:
                # Получаем медикаменты для назначения
                assignment.medications = Medication.objects.filter(
                    medication_id__in=IncludesReception.objects.filter(purpose_id=assignment.purpose_id).values('medication_id')
                )

                # Получаем процедуры для назначения
                assignment.procedures = Procedures.objects.filter(
                    procedures_id__in=IncludesConducting.objects.filter(purpose_id=assignment.purpose_id).values('procedures_id')
                )

                # Получаем врача и помощника для каждого назначения
                assignment.doctor = MedicalStaff.objects.get(medical_staff_id=assignment.medical_staff_id)

                # Получаем медсестру или медбрата как помощника
                assignment.assistant = MedicalStaff.objects.filter(
                    medical_staff_post__in=['Медсестра', 'Медбрат'],
                    user=assignment.medical_staff.user
                ).first()

    return render(request, 'main/assignments.html', {
        'assignments': assignments,
        'staff': staff,
    })


@login_required
def hospitalizations_view(request):
    staff = MedicalStaff.objects.get(user=request.user)

    # Если главный врач, показываем все госпитализации
    if staff.medical_staff_post == 'Главврач':
        hospitalizations = Hospitalization.objects.all()
    else:
        # Для остальных — только госпитализации этого врача
        hospitalizations = Hospitalization.objects.filter(medical_staff=staff)

    return render(request, 'main/hospitalizations.html', {
        'hospitalizations': hospitalizations,
        'staff': staff,
    })

def export_assignments(request):
    # Создание ответа с типом контента для CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assignments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Пациент', 'Дата начала', 'Длительность', 'Статус', 'Диагноз', 'Лечащий врач'])

    # Получаем все назначения для главного врача или для текущего сотрудника
    assignments = Purpose.objects.all().select_related('hospitalization', 'hospitalization__patient', 'hospitalization__medical_staff')

    for assignment in assignments:
        writer.writerow([
            assignment.hospitalization.patient.patient_name,
            assignment.purpose_startdate,
            assignment.purpose_duration,
            assignment.purpose_status,
            assignment.purpose_diagnosis,
            assignment.hospitalization.medical_staff.medical_staff_name  # Лечащий врач
        ])
    
    return response

@login_required
def active_procedures_view(request):
    # Получаем активные назначения для текущего пользователя
    medical_staff = MedicalStaff.objects.get(user=request.user)
    active_purposes = Purpose.objects.filter(
        medical_staff=medical_staff,
        purpose_status="Активный",
        purpose_startdate__lte=date.today(),
        purpose_startdate__gte=date.today() - timedelta(days=1)
    )

    active_procedures = []
    
    # Получаем связанные с ними процедуры
    for purpose in active_purposes:
        procedures = IncludesConducting.objects.filter(purpose=purpose)
        for procedure in procedures:
            active_procedures.append(procedure.procedures)

    return render(request, 'main/procedures.html', {
        'active_procedures': active_procedures
    })

@login_required
def procedures_view(request):
    staff = MedicalStaff.objects.get(user=request.user) 
    
    if staff.medical_staff_post == 'Главврач':
        procedures_executions = ProceduresExecution.objects.all() 
    else:
        procedures_executions = ProceduresExecution.objects.filter(medical_staff_id=staff)

    if request.method == 'POST':
        form = AddProcedureExecutionForm(request.POST)
        if form.is_valid():
            procedure_execution = form.save(commit=False)
            procedure_execution.medical_staff_id = staff
            procedure_execution.procedures_execution_date = date.today()
            procedure_execution.save()
            messages.success(request, "Процедура успешно добавлена!")
            return redirect('procedures')  
    else:
        form = AddProcedureExecutionForm()

    return render(request, 'main/procedures.html', {
        'procedures_executions': procedures_executions,
        'form': form,
    })
@login_required
def medications_view(request):
    staff = MedicalStaff.objects.get(user=request.user) 

    if staff.medical_staff_post == 'Главврач':
        medication_dispensing_records = MedicationDispensing.objects.all()  
    else:
        medication_dispensing_records = MedicationDispensing.objects.filter(medical_staff=staff)  

    if request.method == 'POST':
        form = MedicationDispensingForm(request.POST)
        if form.is_valid():
            medication_dispensing = form.save(commit=False)
            medication_dispensing.medical_staff = staff
            medication_dispensing.medication_dispensing_date = date.today()  # Текущая дата
            medication_dispensing.save()
            messages.success(request, "Медикамент успешно выдан!")
            return redirect('medications')  # Перенаправление на страницу с медикаментами
    else:
        form = MedicationDispensingForm()

    return render(request, 'main/medications.html', {
        'medication_dispensing_records': medication_dispensing_records,  # Все или только свои записи
        'form': form,
    })


@login_required
def add_procedure_execution(request):
    
    procedures_list = Procedures.objects.all()

    if request.method == 'POST':
        procedure_id = request.POST.get('procedure_id')
        duration = request.POST.get('procedures_execution_duration')
        comment = request.POST.get('procedures_execution_comment')
        status = request.POST.get('procedures_execution_status')

        try:
            procedure = Procedures.objects.get(id=procedure_id)  # Получаем процедуру по ID
        except Procedures.DoesNotExist:
            messages.error(request, "Процедура не найдена!")
            return redirect('add_procedure_execution')

        # Создаем запись в ProceduresExecution
        try:
            ProceduresExecution.objects.create(
                procedures_execution_date=date.today(),
                procedures_execution_comment=comment,
                medical_staff_id=request.user.medical_staff_id,  # Текущий пользователь
                procedures_id=procedure,  # Процедура, которую выбрал пользователь
                procedures_execution_status=status,
                procedures_execution_duration=duration
            )
            messages.success(request, "Процедура успешно добавлена!")
            return redirect('procedures_list')  # Перенаправление на список процедур
        except Exception as e:
            messages.error(request, f"Ошибка при добавлении процедуры: {str(e)}")
            return redirect('add_procedure_execution')

    return render(request, 'procedures.html', {'procedures_list': procedures_list})
@login_required
def procedures_view(request):
    staff = MedicalStaff.objects.get(user=request.user)  

    if staff.medical_staff_post == 'Главврач':
        procedures_executions = ProceduresExecution.objects.all() 
    else:
        procedures_executions = ProceduresExecution.objects.filter(medical_staff_id=staff)  

    if request.method == 'POST':
        form = AddProcedureExecutionForm(request.POST)
        if form.is_valid():
            procedure_execution = form.save(commit=False)
            procedure_execution.medical_staff_id = staff
            procedure_execution.procedures_execution_date = date.today()
            procedure_execution.save()
            messages.success(request, "Процедура успешно добавлена!")
            return redirect('procedures')  
    else:
        form = AddProcedureExecutionForm()

    return render(request, 'main/procedures.html', {
        'procedures_executions': procedures_executions, 
        'form': form,
    })


@login_required
def add_medication_dispensing(request):
    staff = MedicalStaff.objects.get(user=request.user)
    
    # Получаем все активные медикаменты
    active_medications = Medication.objects.filter(
        purpose__purpose_status__in=['Активный', 'Приостановлен'],
        purpose__purpose_startdate__lte=date.today(),  # Начало назначения до сегодняшнего дня
        purpose__purpose_enddate__gte=date.today()  # Конец назначения после сегодняшнего дня
    )

    if request.method == 'POST':
        form = MedicationDispensingForm(request.POST)
        if form.is_valid():
            medication_dispensing = form.save(commit=False)
            medication_dispensing.medical_staff = staff  # Текущий медицинский сотрудник
            medication_dispensing.medication_dispensing_date = date.today()  # Текущая дата
            medication_dispensing.save()
            return redirect('medications_list')  # Перенаправляем на список медикаментов

    else:
        form = MedicationDispensingForm()

    return render(request, 'main/medication_dispensing_form.html', {
        'form': form,
        'active_medications': active_medications,
    })

def save_procedure(request):
    # Проверка метода запроса
    if request.method == 'POST':
        form = ProceduresExecutionForm(request.POST)
        
        # Проверка валидности формы
        if form.is_valid():
            # Сохраняем данные в базе данных
            procedure_execution = form.save(commit=False)
            
            # Дополнительно можно установить данные по текущему пользователю, если нужно
            # procedure_execution.medical_staff_id = request.user.medical_staff_id
            
            # Сохраняем запись
            procedure_execution.save()
            
            messages.success(request, 'Процедура успешно сохранена!')
            return redirect('procedures_list')  # Перенаправление на список процедур
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ProceduresExecutionForm()

    return render(request, 'main/procedure_form.html', {'form': form})
