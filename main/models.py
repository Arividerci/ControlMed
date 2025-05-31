from django.db import models
from django.contrib.auth.models import User

class MedicalStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    medical_staff_name = models.CharField(max_length=150)
    medical_staff_birthday = models.DateField()
    medical_staff_gender = models.CharField(max_length=3)
    medical_staff_post = models.CharField(max_length=100)
    medical_staff_specialisation = models.CharField(max_length=100)
    medical_staff_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'medical_staff'
        managed = True

class Hospitalization(models.Model):
    hospitalization_id = models.AutoField(primary_key=True)
    hospitalization_startdate = models.DateField()  
    hospitalization_room = models.SmallIntegerField()
    hospitalization_enddate = models.DateField()   
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.RESTRICT, db_column='medical_staff_id')
    patient = models.ForeignKey('Patient',   on_delete=models.CASCADE, db_column='patient_id')

    class Meta:
        db_table = 'hospitalization'
        managed = False

class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=150)
    patient_birthday = models.DateField()
    patient_gender = models.CharField(max_length=10)
    patient_weight = models.DecimalField(max_digits=5, decimal_places=2)
    patient_height = models.IntegerField()
    patient_blood_type = models.CharField(max_length=3)
    patient_photo = models.ImageField(upload_to='patient_photos/', default='no-photo.webp', blank=True, null=True)

    class Meta:
        db_table = 'patient'


class Purpose(models.Model):
    purpose_id = models.AutoField(primary_key=True)
    purpose_StartDate = models.DateField()
    purpose_duration = models.SmallIntegerField()
    purpose_status = models.CharField(max_length=100)
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.RESTRICT, db_column='medical_staff_id')
    hospitalization = models.ForeignKey(Hospitalization, on_delete=models.RESTRICT, db_column='hospitalization_id')
    purpose_diagnosis = models.TextField(max_length=1500)

    class Meta:
        db_table = 'purpose'
        managed = False


class MedicalBook(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    medicalbook_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'medicalbook'
        managed = False

class MedicalBookContent(models.Model):
    medicalbook_id = models.AutoField(primary_key=True)
    medicalbook_id = models.IntegerField()  
    purpose_id = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')
    medicalbook_content_notes = models.TextField(max_length=1500, null=True, blank=True)

    class Meta:
        db_table = 'medicalbook_content'
        managed = False

class Medication(models.Model):
    medication_id = models.AutoField(primary_key=True)
    medication_name = models.CharField(max_length=150)
    medication_dose = models.SmallIntegerField()

    class Meta:
        db_table = 'medication'
        managed = False

class MedicationDispensing(models.Model):
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.RESTRICT, db_column='medical_staff_id')
    medication = models.ForeignKey(Medication, on_delete=models.RESTRICT, db_column='medication_id')
    medication_dispensing_date = models.DateField()
    medication_dispensing_status = models.CharField(max_length=20)
    medication_dispensing_dose = models.IntegerField(null=True, blank=True)
    medication_dispensing_com = models.TextField(max_length=1500, null=True, blank=True)

    class Meta:
        db_table = 'medication_dispensing'
        managed = False
        unique_together = (('medical_staff', 'medication'),)

class Procedures(models.Model):
    procedures_id = models.AutoField(primary_key=True)
    procedures_name = models.CharField(max_length=100)
    procedures_duration = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        db_table = 'procedures'
        managed = False

class ProceduresExecution(models.Model):
    procedures = models.ForeignKey(Procedures, on_delete=models.RESTRICT, db_column='procedures_id')
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.RESTRICT, db_column='medical_staff_id')
    procedures_execution_date = models.DateField()
    procedures_execution_status = models.CharField(max_length=20)
    procedures_execution_duration = models.IntegerField(null=True, blank=True)
    procedures_execution_com = models.TextField(max_length=1500, null=True, blank=True)

    class Meta:
        db_table = 'procedures_execution'
        managed = False
        unique_together = (('procedures', 'medical_staff'),)

class IncludesConducting(models.Model):
    procedures = models.ForeignKey(Procedures, on_delete=models.RESTRICT, db_column='procedures_id')
    purpose = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')

    class Meta:
        db_table = 'Includes_conducting'
        managed = False
        unique_together = (('procedures', 'purpose'),)

class IncludesReception(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.RESTRICT, db_column='medication_id')
    purpose = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')

    class Meta:
        db_table = 'Includes_reception'
        managed = False
        unique_together = (('medication', 'purpose'),)
