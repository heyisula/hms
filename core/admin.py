from django.contrib import admin
from .models import (
    Department,
    Doctor,
    Patient,
    Appointment,
    MedicalRecord,
    UserProfile,
)


# ──────────────────────────────────────────────
# Inlines
# ──────────────────────────────────────────────
class MedicalRecordInline(admin.TabularInline):
    """Show medical records inside a Patient's detail page."""
    model = MedicalRecord
    extra = 0
    fields = ('doctor', 'appointment', 'diagnosis', 'prescription', 'created_at')
    readonly_fields = ('created_at',)


class AppointmentInline(admin.TabularInline):
    """Show appointments inside a Patient's detail page."""
    model = Appointment
    extra = 0
    fields = ('doctor', 'date', 'time', 'status', 'reason')


# ──────────────────────────────────────────────
# Model Admins
# ──────────────────────────────────────────────
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'department', 'phone', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('first_name', 'last_name', 'specialization')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'gender', 'blood_group', 'registration_date')
    list_filter = ('gender', 'blood_group')
    search_fields = ('first_name', 'last_name', 'phone')
    inlines = [AppointmentInline, MedicalRecordInline]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__last_name')
    date_hierarchy = 'date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
