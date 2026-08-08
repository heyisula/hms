from django.db import models
from django.contrib.auth.models import User


# ──────────────────────────────────────────────
# Department
# ──────────────────────────────────────────────
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# Doctor
# ──────────────────────────────────────────────
class Doctor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True,
        help_text="Link to a Django login account (optional).",
    )
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="doctors",
    )
    phone = models.CharField(max_length=20, blank=True)
    availability = models.TextField(
        blank=True,
        help_text="Free-text schedule, e.g. 'Mon-Fri 09:00-17:00'.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


# ──────────────────────────────────────────────
# Patient
# ──────────────────────────────────────────────
class Patient(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(
        max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True,
    )
    registration_date = models.DateField(auto_now_add=True)
    emergency_contact = models.CharField(
        max_length=150, blank=True,
        help_text="Name and phone of emergency contact.",
    )

    class Meta:
        ordering = ["-registration_date", "name"]

    def __str__(self):
        return f"{self.name} ({self.gender})"


# ──────────────────────────────────────────────
# Appointment
# ──────────────────────────────────────────────
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments",
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments",
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default="scheduled",
    )
    reason = models.TextField(blank=True, verbose_name="Reason for visit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "Appointment"

    def __str__(self):
        return (
            f"{self.patient.name} → Dr. {self.doctor.name} "
            f"on {self.date} @ {self.time:%H:%M} [{self.get_status_display()}]"
        )


# ──────────────────────────────────────────────
# Medical Record
# ──────────────────────────────────────────────
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_records",
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, related_name="medical_records",
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="records",
        help_text="The appointment this record was created from (if any).",
    )
    diagnosis = models.CharField(max_length=300)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Medical Record"

    def __str__(self):
        return f"Record #{self.pk} – {self.patient.name}: {self.diagnosis[:50]}"


# ──────────────────────────────────────────────
# User Profile (role extension for Django User)
# ──────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("doctor", "Doctor"),
        ("nurse", "Nurse"),
        ("receptionist", "Receptionist"),
        ("lab_staff", "Lab Staff"),
        ("pharmacist", "Pharmacist"),
        ("accountant", "Accountant"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="receptionist")
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return f"{self.user.username} – {self.get_role_display()}"
