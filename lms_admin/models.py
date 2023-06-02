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
    is_completed = models.BooleanField(default=False)
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
    