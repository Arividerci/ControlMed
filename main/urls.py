from django.urls import path
from . import views
from main.views import login_view
from .views import add_patient
from django.conf import settings
from django.conf.urls.static import static
from .views import delete_selected_patients
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('appointments/', views.appointments, name='appointments'),
    path('patients/', views.patients, name='patients'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'), 
    path('add-patient/', add_patient, name='add_patient'),
    path('patients/delete-selected/', views.delete_selected_patients, name='delete_selected_patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('patients/remove-photo/<int:patient_id>/', views.remove_patient_photo, name='remove_patient_photo'),
    path('patients/<int:patient_id>/hospitalization/', views.patient_hospitalization, name='patient_hospitalization'),
    path('patients/<int:patient_id>/purpose/', views.patient_purpose, name='patient_purpose'),
    path('patients/<int:patient_id>/purpose/save/', views.save_purpose_row, name='save_purpose_row'),
    path('patients/<int:patient_id>/purpose/delete/<int:purpose_id>/', views.delete_purpose_row, name='delete_purpose_row'),
    path('patients/<int:patient_id>/medbook/', views.patient_medbook, name='patient_medbook'),
    path('patients/<int:patient_id>/medbook/comment/<int:content_id>/update/',views.update_medical_book_comment, name='update_medical_book_comment' ),
    path('assignments/', views.assignments_view, name='assignments'),
    path('hospitalizations/', views.hospitalizations_view, name='hospitalizations'),
    path('procedures/', views.procedures_view, name='procedures'),
    path('assignments/export/', views.export_assignments, name='export_assignments'),
    path('patients/<int:patient_id>/hospitalization/', views.add_hospitalization, name='add_hospitalization'),
    path('active_procedures/', views.active_procedures_view, name='active_procedures'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('generate_hospitalization_report/', views.generate_hospitalization_report, name='generate_hospitalization_report'),
    path('save_procedure/', views.save_procedure, name='save_procedure'),
    path('procedures_list/', views.procedures_view, name='procedures_list'),
    path('add_procedure_execution/', views.add_procedure_execution, name='add_procedure_execution'),
    path('medications/', views.medications_view, name='medications'),
    path('medications/', views.medications_view, name='medications'),
    path('delete-account/', views.delete_medical_staff, name='delete_medical_staff'),
    path('generate_selected_patients_report/', views.generate_selected_patients_report, name='generate_selected_patients_report'),


]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
