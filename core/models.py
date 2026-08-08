from django.db import models
from django.conf import settings
from django.utils import timezone


# ──────────────────────────────────────────────
# Department
# ──────────────────────────────────────────────
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# Doctor
# ──────────────────────────────────────────────
class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        null=True,
        blank=True,
        help_text='Link to Django login account (optional).',
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
    )
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    availability = models.TextField(
        blank=True,
        help_text='Free-text schedule, e.g. "Mon–Fri 9 AM – 5 PM"',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name} ({self.specialization})'


# ──────────────────────────────────────────────
# Patient
# ──────────────────────────────────────────────
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A−'),
        ('B+', 'B+'),
        ('B-', 'B−'),
        ('AB+', 'AB+'),
        ('AB-', 'AB−'),
        ('O+', 'O+'),
        ('O-', 'O−'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(
        max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True,
    )
    registration_date = models.DateField(default=timezone.now)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone})'


# ──────────────────────────────────────────────
# Appointment
# ──────────────────────────────────────────────
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='appointments',
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='appointments',
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default='scheduled',
    )
    reason = models.TextField(
        blank=True, help_text='Reason for visit / chief complaint',
    )
    notes = models.TextField(blank=True, help_text='Internal staff notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return (
            f'{self.patient} → Dr. {self.doctor.last_name} '
            f'on {self.date} at {self.time:%H:%M}'
        )


# ──────────────────────────────────────────────
# Medical Record
# ──────────────────────────────────────────────
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='medical_records',
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records',
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records',
    )
    diagnosis = models.CharField(max_length=255)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'

    def __str__(self):
        return f'{self.patient} — {self.diagnosis} ({self.created_at:%Y-%m-%d})'


# ──────────────────────────────────────────────
# User Profile (role-based, extends auth.User)
# ──────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('lab_staff', 'Lab Staff'),
        ('pharmacist', 'Pharmacist'),
        ('accountant', 'Accountant'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.get_role_display()}'
