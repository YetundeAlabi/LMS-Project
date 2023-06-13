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
from accounts.models import Tutor, Student
from lms_admin.models import Track
from django.db.models import Sum
from .fields import OrderField

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class BaseContent(models.Model):
    title = models.CharField(max_length=225, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
         
class Course(BaseContent):
    course_tutor=models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True)
    track=models.ForeignKey(Track, on_delete=models.SET_NULL, null=True)
    slug= models.SlugField(unique=True, blank=True, null=True)
    
    class Meta:
        indexes = [ models.Index(fields=['track','slug'])]
       

    def __str__(self):
        return f"{self.title}"
    
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
        if self.is_active:
            if not self.pk:
                max_order_active = Topic.objects.filter(course=self.course, is_active=True).aggregate(models.Max('order'))[
                    'order__max']
                max_order_inactive = Topic.objects.filter(course=self.course, is_active=False).aggregate(models.Max('order'))[
                    'order__max']

                if max_order_active is not None:
                    if max_order_inactive is not None and max_order_inactive > max_order_active:
                        self.order = max_order_inactive + 1
                    else:
                        self.order = max_order_active + 1
                else:
                    self.order = 1
        else:
            if self.order is not None:
                # Existing object marked as inactive, shift down the order for subsequent active topics
                topics_to_reorder = Topic.objects.filter(course=self.course, is_active=True, order__gt=self.order)

                for topic in topics_to_reorder:
                    topic.order -= 1
                    topic.save()

                self.order = None

        return super().save(*args, **kwargs)

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
    text = models.TextField(blank=True, null=True)


class File(BaseContent):
    file = models.FileField(upload_to='files')

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


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        topic_count = self.student_topics.filter(student_course=self).count()
        topic_progress_sum = self.student_topics.filter(student_course=self).aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
        if topic_count > 0:
            average_progress = topic_progress_sum / topic_count
            self.progress_level = average_progress
            self.save()

    def __str__(self):
        return f' {self.course.title} for {self.student}'


class StudentTopic(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='student_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        sub_topic_count = self.student_subtopics.filter(student_topic=self).count()
        sub_topic_progress_sum = self.student_subtopics.filter(student_topic=self).aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
        if sub_topic_count > 0:
            average_progress = sub_topic_progress_sum / sub_topic_count
            self.progress_level = average_progress
            self.save()

    def __str__(self):
        return f'{self.student_course}, {self.topic.title}'


class StudentSubTopic(models.Model):
    student_topic = models.ForeignKey(StudentTopic, on_delete=models.CASCADE, related_name='student_subtopics')
    sub_topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.00)

    def update_progress_level(self):
        if self.progress_level < 100:
            self.progress_level = 100
            self.save()

    def __str__(self):
        return f"student subtopic {self.id} , under {self.student_topic}"

