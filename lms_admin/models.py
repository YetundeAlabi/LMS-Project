from django.db import models
from django.urls import reverse
from django.db.models.query import QuerySet

# Create your models here.

class ActiveManager(models.Manager):
 def get_queryset(self):
    return super(ActiveManager, self).get_queryset().filter(is_delete=False)

class DeleteManager(models.Manager):
 def get_queryset(self):
    return super(ActiveManager, self).get_queryset().filter(is_delete=True)
     

class Track(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeleteManager()

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('track_detail', kwargs={'slug': self.slug})


class Cohort(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def get_name(self) -> str:
        return f'Cohort of {self.year}'
    
    def __str__(self):
        return self.get_name



class ApprovedApplicantManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)


class NotApprovedApplicantManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_approved=False)
    

class Applicant(models.Model):
    GENDER_CHOICES =(
        ("FEMALE", "Female"),
        ("MALE", "Male"),
    )
    first_name = models.CharField(max_length=150)
    cohort = models.ForeignKey('Cohort', on_delete=models.SET_NULL, related_name='applicants')
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    track = models.ForeignKey("Track", on_delete=models.SET_NULL, related_name="applicants", null=True)
    is_approved = models.BooleanField(default=False)
    objects = models.Manager()
    approved = ApprovedApplicantManager()
    not_approved= NotApprovedApplicantManager()