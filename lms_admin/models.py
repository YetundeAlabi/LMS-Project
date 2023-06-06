from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.

class ActiveManager(models.Manager):
 def get_queryset(self):
    return super(ActiveManager, self).get_queryset().filter(is_deleted=False)

class DeleteManager(models.Manager):
 def get_queryset(self):
    return super(ActiveManager, self).get_queryset().filter(is_deleted=True)
     

class Track(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(null=True, blank=True)
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
        return reverse('lms_admin:track_detail', kwargs={'slug': self.slug})


class Cohort(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def get_name(self) -> str:
        return f'Cohort of {self.year}'
    
    def __str__(self):
        return self.get_name()



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
    cohort = models.ForeignKey('Cohort', on_delete=models.SET_NULL, related_name='applicants', null=True)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    track = models.ForeignKey("Track", on_delete=models.SET_NULL, related_name="applicants", null=True)
    is_approved = models.BooleanField(default=False)
    objects = models.Manager()
    approved = ApprovedApplicantManager()
    not_approved= NotApprovedApplicantManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


@receiver(post_save, sender=Track)
def track_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        slug = slugify(instance.name)
        instance.slug = slug
        instance.save()