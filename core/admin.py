from django.contrib import admin
from .models import (
    Department, Doctor, Patient, Appointment, MedicalRecord, UserProfile,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "department", "phone")
    list_filter = ("department", "specialization")
    search_fields = ("name", "specialization")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "date_of_birth", "gender", "blood_group", "phone", "registration_date")
    list_filter = ("gender", "blood_group")
    search_fields = ("name", "phone")
    date_hierarchy = "registration_date"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "time", "status")
    list_filter = ("status", "date", "doctor")
    search_fields = ("patient__name", "doctor__name", "reason")
    date_hierarchy = "date"


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "diagnosis", "created_at")
    list_filter = ("created_at",)
    search_fields = ("patient__name", "diagnosis")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone")
    list_filter = ("role",)
    search_fields = ("user__username",)
