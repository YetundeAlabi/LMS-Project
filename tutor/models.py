import uuid
from django.db import models
from django.db.models import F, Max
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.text import slugify
from accounts.models import Tutor
from .fields import OrderField
from lms_admin.models import Track

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class BaseContent(models.Model):
    title=models.CharField(max_length=225, blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    is_active=models.BooleanField(default=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects=ActiveManager()

    class Meta:
        abstract = True
         
class Course(BaseContent):
    course_tutor=models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True)
    track=models.ForeignKey(Track, on_delete=models.SET_NULL, null=True)
    slug= models.SlugField(unique=True, blank=True, null=True)
    order = OrderField(blank=True, for_fields=['title'])
    
    class Meta:
        ordering= ['order']
        indexes = [ models.Index(fields=['track','slug'])]
       

    def __str__(self):
        return f"{self.order}_{self.title}"
    
    def get_absolute_url(self):
        return reverse('course_detail', args=[str(self.slug)])


class Topic(BaseContent):
    course=models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
    id=models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    order = OrderField(blank=True, for_fields=['course'])
    
    class Meta:
        ordering= ['order']
        
    def __str__(self):
        return f"{self.order}_{self.title}"
    
  

def save(self, *args, **kwargs):
    if not self.is_active:
        max_order = Topic.active_objects.aggregate(max_order=Max('order')).get('max_order', 0)
        self.order = max_order
        Topic.active_objects.filter(order__gt=0).update(order=F('order') - 1)
        self.order = 0
    else:
        Topic.active_objects.update(order=F('order') + 1)  
        max_order = Topic.active_objects.aggregate(max_order=Max('order')).get('max_order', 0)
        self.order = max_order + 1

    super().save(*args, **kwargs)


class SubTopic(BaseContent):
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('text', 'file', 'video')}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['topic'])

    class Meta:
        ordering= ['order']
        
    def __str__(self):
        return f"{self.order}_{self.object_id}"
  
    
class Text(BaseContent):
    text =models.TextField(blank=True, null=True)


class File(BaseContent):
    file=models.FileField(upload_to='files')

    def get_file_url(self):
        return self.file.url

class Video(BaseContent):
    url = models.URLField()


@receiver(post_save, sender=Course)
def course_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        slug = slugify(instance.title)
        instance.slug = slug
        instance.save()