from django.contrib import admin
from lms_admin.models import Track

# Register your models here.
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description', 'is_completed',]
    list_filter = [ 'created_date',]
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['created_date']   