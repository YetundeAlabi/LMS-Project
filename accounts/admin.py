from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import SignUpForm
from .models import User, Student, Tutor
# Register your models here.
class UserAdmin(BaseUserAdmin):
    add_form = SignUpForm

    ordering = ('email',)  # Set the ordering field to 'email'
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')  # Add 'role', 'is_staff', and 'is_active' to the list_display field
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')  # Add 'role' to the list_filter field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    # list_display = ["email", "first_name", "last_name"]


    # fieldsets = [
    #     (None, {"fields": ["email", "password"]}),
    #     ("Personal info", {"fields": [
    #      "first_name", "last_name"]}),
    #     ("Permissions", {"fields": ["is_active"]}),
    #     ("Dates", {"fields": ["last_login",]})
    # ]

    # add_fieldsets = [
    #     (
    #         None,
    #         {
    #             "classes": ["wide"],
    #             "fields": ["email", "first_name", "last_name", "password1", "password2"],
    #         },
    #     ),
    # ]


# search_fields = ("email",)


admin.site.register(User, UserAdmin)

admin.site.register(Student)
admin.site.register(Tutor)
