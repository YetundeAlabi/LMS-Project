from django.contrib import admin
from lms_admin.models import Track, Applicant

# Register your models here.
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description',]
    list_filter = [ 'created_date',]
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['created_date']   
from django.contrib import admin
from .models import Cohort

# Register your models here.
admin.site.register(Cohort)
admin.site.register(Applicant)

