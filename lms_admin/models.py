from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import RegexValidator

from phonenumber_field.modelfields import PhoneNumberField

from base.managers import ApprovedManager, UnApprovedManager
from base import constants
from base.models import DeletableBaseModel

# Create your models here.

class Track(DeletableBaseModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)    

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('lms_admin:track_detail', kwargs={'slug': self.slug})
    
    def get_students_count(self):
        return self.students.count()


class Cohort(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def get_name(self) -> str:
        return f'Cohort of {self.year}'
    
    def __str__(self):
        return self.get_name()
    
    def get_students_count(self):
        return self.students.count()
    

class NigerianPhoneNumberField(PhoneNumberField):
    default_validators = [
        RegexValidator(
            r"^(?:\+?234|0)[789]\d{9}$",
            message="Please enter a valid Nigerian phone number starting with +234.",
            code="invalid_phone_number",
        ),
    ]

    def formfield(self, **kwargs):
        defaults = {
            "validators": self.default_validators,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
class Applicant(models.Model):
    FEMALE = constants.FEMALE
    MALE = constants.MALE

    GENDER_CHOICES =(
        ('F', FEMALE),
        ('M', MALE),
    )

    first_name = models.CharField(max_length=150)
    cohort = models.ForeignKey('Cohort', on_delete=models.SET_NULL, related_name='applicants', null=True)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    track = models.ForeignKey("Track", on_delete=models.SET_NULL, related_name="applicants", null=True)
    is_approved = models.BooleanField(default=False)
    applied_date = models.DateTimeField(auto_now_add=True, null=True)
    phone_number = NigerianPhoneNumberField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    objects = models.Manager()
    approved = ApprovedManager()
    not_approved= UnApprovedManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

