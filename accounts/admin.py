from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile, ParentProfile

@admin.action(description="Verify selected doctor medical licenses")
def verify_doctor_licenses(modeladmin, request, queryset):
    queryset.update(is_verified=True)

class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'

class ParentProfileInline(admin.StackedInline):
    model = ParentProfile
    can_delete = False
    verbose_name_plural = 'Parent Profile'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Telemedicine Role', {'fields': ('role', 'phone_number')}),
    )

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'specialization', 'experience_years', 'consultation_fee', 'is_verified')
    list_filter = ('is_verified', 'specialization')
    search_fields = ('user__username', 'user__email', 'license_number', 'specialization')
    actions = [verify_doctor_licenses]

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'emergency_contact', 'preferred_language', 'consent_to_telehealth')
    search_fields = ('user__username', 'user__email', 'emergency_contact')
