from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminCreateForm
from .models import User, Student, Tutor
# Register your models here.
# class UserAdmin(BaseUserAdmin):
    # add_form = AdminCreateForm
#     list_display = ["email", "first_name", "last_name", "username"]

#     list_filter = ["is_staff"]

#     fieldsets = [
#         (None, {"fields": ["email", "password"]}),
#         ("Personal info", {"fields": [
#          "first_name", "last_name"]}),
#         ("Permissions", {"fields": ["is_active", "is_staff"]}),
#         ("Dates", {"fields": ["last_login",]})
#     ]

#     add_fieldsets = [
#         (
#             None,
#             {
#                 "classes": ["wide"],
#                 "fields": ["email", "first_name", "last_name", "password1", "password2"],
#             },
#         ),
#     ]


# search_fields = ("email",)
# ordering = ("email",)

admin.site.register(User)

admin.site.register(Student)
admin.site.register(Tutor)
