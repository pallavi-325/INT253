from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'doctor', 'parent', 'scheduled_date', 'scheduled_time', 'status', 'severity')
    list_filter = ('status', 'severity', 'scheduled_date')
    search_fields = ('child__first_name', 'child__last_name', 'doctor__username', 'parent__username', 'chief_complaint')
    date_hierarchy = 'scheduled_date'
