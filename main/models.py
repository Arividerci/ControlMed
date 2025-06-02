from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

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
        managed = False

class Hospitalization(models.Model):
    hospitalization_id = models.AutoField(primary_key=True)
    hospitalization_startdate = models.DateField()  
    hospitalization_room = models.SmallIntegerField()
    hospitalization_enddate = models.DateField()   
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.CASCADE, db_column='medical_staff_id')
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
        managed = False

class Purpose(models.Model):
    purpose_id = models.AutoField(primary_key=True)
    purpose_startdate = models.DateField()
    purpose_duration = models.SmallIntegerField()
    purpose_status = models.CharField(max_length=100)
    medical_staff = models.ForeignKey(MedicalStaff, on_delete=models.RESTRICT, db_column='medical_staff_id')
    hospitalization = models.ForeignKey(Hospitalization, on_delete=models.RESTRICT, db_column='hospitalization_id')
    purpose_diagnosis = models.TextField(max_length=1500)

    def get_status(self):
        if self.purpose_startdate + timedelta(days=self.purpose_duration) >= date.today():
            return "Активный"
        return "Завершено"

    def save(self, *args, **kwargs):
        self.purpose_status = self.get_status()
        super().save(*args, **kwargs)

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
    medical_book_content_id = models.AutoField(primary_key=True)  
    medicalbook_id = models.IntegerField()  
    purpose = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')
    medical_book_content_notes = models.TextField(max_length=1500, null=True, blank=True)

    class Meta:
        db_table = 'medical_book_content'
        managed = False

class Medication(models.Model):
    medication_id = models.AutoField(primary_key=True)
    medication_name = models.CharField(max_length=150)
    medication_dose = models.SmallIntegerField()
    def __str__(self):
        return self.medication_name  
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

    def __str__(self):
        return self.procedures_name  # Возвращаем имя процедуры
    
    class Meta:
        db_table = 'procedures'
        managed = False

class IncludesReception(models.Model):
    medication = models.ForeignKey(
        Medication, on_delete=models.RESTRICT, db_column='medication_id', primary_key=True
    )
    purpose = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')

    def save(self, *args, **kwargs):
        raise NotImplementedError("Нельзя использовать save(). Используй bulk_create.")

    class Meta:
        db_table = 'includes_reception'
        managed = False
        unique_together = (('medication', 'purpose'),)

class IncludesConducting(models.Model):
    procedures = models.ForeignKey(
        Procedures, on_delete=models.RESTRICT, db_column='procedures_id', primary_key=True
    )
    purpose = models.ForeignKey(Purpose, on_delete=models.RESTRICT, db_column='purpose_id')

    def save(self, *args, **kwargs):
        raise NotImplementedError("Нельзя использовать save(). Используй bulk_create.")

    class Meta:
        db_table = 'includes_conducting'
        managed = False
        unique_together = (('procedures', 'purpose'),)


class ProceduresExecution(models.Model):
    procedures_execution_id = models.AutoField(primary_key=True)  # Уникальный идентификатор для выполнения процедуры
    procedures_id = models.ForeignKey('Procedures', on_delete=models.RESTRICT, db_column='procedures_id')  # Внешний ключ на модель Procedures
    medical_staff_id = models.ForeignKey('MedicalStaff', on_delete=models.RESTRICT, db_column='medical_staff_id')  # Внешний ключ на модель MedicalStaff (врач, медсестра и т. д.)
    procedures_execution_date = models.DateField(default=date.today)  # Дата выполнения процедуры
    procedures_execution_duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Продолжительность выполнения процедуры
    procedures_execution_status = models.CharField(max_length=20, default='В ожидании')  # Статус выполнения процедуры
    procedures_execution_comment  = models.CharField(max_length=1500)

    def __str__(self):
        return f"Процедура {self.procedures_id.procedures_name} ({self.procedures_execution_status})"

    class Meta:
        db_table = 'procedures_execution'
        managed = False
        
class MedicationDispensing(models.Model):
    medication_dispensing_id = models.AutoField(primary_key=True)
    medication_id = models.ForeignKey('Medication', on_delete=models.RESTRICT, db_column='medication_id')  # Внешний ключ на модель Medication
    medical_staff_id = models.ForeignKey('MedicalStaff', on_delete=models.RESTRICT, db_column='medical_staff_id')  # Внешний ключ на модель MedicalStaff
    medication_dispensing_date = models.DateField(default=date.today)  # Дата выдачи медикамента
    medication_dispensing_dose = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Доза медикамента
    medication_dispensing_status = models.CharField(max_length=20, default='В ожидании')  # Статус выдачи
    medication_dispensing_comment = models.CharField(max_length=1500)

    def __str__(self):
        return f"Выдача {self.medication.medication_name} ({self.medication_dispensing_status})"

    class Meta:
        db_table = 'medication_dispensing'
        managed = False