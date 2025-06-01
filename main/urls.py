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
    path('medications/', views.medications_view, name='medications'),
 

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
