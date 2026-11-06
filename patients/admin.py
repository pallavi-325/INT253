from django.contrib import admin
from .models import ChildProfile, SkinImage

class SkinImageInline(admin.TabularInline):
    model = SkinImage
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'parent', 'date_of_birth', 'gender', 'blood_group', 'created_at')
    list_filter = ('gender', 'blood_group')
    search_fields = ('first_name', 'last_name', 'parent__username', 'parent__email')
    inlines = [SkinImageInline]

@admin.register(SkinImage)
class SkinImageAdmin(admin.ModelAdmin):
    list_display = ('child', 'body_part', 'view_type', 'uploaded_at')
    list_filter = ('body_part', 'view_type', 'uploaded_at')
    search_fields = ('child__first_name', 'child__last_name', 'notes')
