from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class IsActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class BaseContent(models.Model):
    title=models.CharField(max_length=225, blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    is_active=models.BooleanField(default=True, blank=True, null=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects=IsActiveManager()


    class Meta:
         abstract = True
         ordering= ['created_at']

        
class Course(BaseContent):
    # course_tutor=models.ForeignKey('Tutor_User', on_delete=models.SET_NULL, null=True)
    # track=models.ForeignKey('Track', on_delete=models.SET_NULL, null=True)
    slug= models.SlugField(blank=True, null=True)


    def __str__(self):
        return self.slug
    
    def get_absolute_url(self):
        return reverse('course-detail', args=[str(self.slug)])


class Topic(BaseContent):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    id=models.UUIDField(primary_key=True, unique=True)


    def __str__(self):
         return f"{self.title}"
    

class SubTopic(BaseContent):
    topic=models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True)
    id=models.UUIDField(primary_key=True, unique=True)
    content_type=models.ForeignKey(ContentType,
                                   on_delete=models.CASCADE,
                                   limit_choices_to={'model__in':(
                                       'text',
                                       'file',
                                       'image',
                                       'video')})
    object_id=models.PositiveIntegerField()
    item = GenericForeignKey('content_type','object_id')


    def __str__(self):
         return f"{self.title}"
    

class Text(BaseContent):
    content=models.TextField(blank=True, null=True)


class File(BaseContent):
    file= models.FileField(upload_to='files')

class Image(BaseContent):
    image=models.ImageField(upload_to='images')

class Video(BaseContent):
    url = models.URLField()


@receiver(post_save, sender=Course)
def course_slug(sender, instance, created, **kwargs):
    if created:
        instance.slug=instance.title.replace(' ','-')
        instance.save()