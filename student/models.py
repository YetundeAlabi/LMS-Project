from accounts.models import Student
from django.db import models
from django.db.models import Sum, Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from tutor.models import Course, SubTopic, Topic, Track

# Create your models here.

class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    slug = models.SlugField()
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        if self.progress_level < 100:
            average_progress= self.student_topics.aggregate(progress_avg=Avg('progress_level'))['progress_avg'] or 0
            self.progress_level = average_progress
            self.save(update_fields=['progress_level'])

    def __str__(self):
        return f' {self.course.title} for {self.student.user.first_name}'
    

class StudentTopic(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='student_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    slug = models.SlugField()
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        if self.progress_level < 100:
            related_sub_topics_progress_avg = self.student_subtopics.aggregate(progress_avg=Avg('progress_level'))['progress_avg'] or 0
            self.progress_level = related_sub_topics_progress_avg
            self.save(update_fields=['progress_level'])

    def __str__(self):
        return f'{self.student_course}, {self.topic.title}'


class StudentSubTopic(models.Model):
    student_topic = models.ForeignKey(StudentTopic, on_delete=models.CASCADE, related_name='student_subtopics')
    sub_topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE)
    slug = models.SlugField()
    progress_level = models.FloatField(default=0.00)

    def update_progress_level(self):
        if self.progress_level < 100:
            self.progress_level = 100
            self.save(update_fields=['progress_level'])

    def __str__(self):
        return f"student subtopic {self.id} , under {self.student_topic}"


@receiver(post_save, sender=StudentCourse)
def student_course_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        slug = slugify(instance.course.title)
        instance.slug = slug
        instance.save()

@receiver(post_save, sender=StudentTopic)
def student_topic_slug(sender, instance, created, **kwargs):
    if created and not instance.slug:
        slug = slugify(instance.topic.title)
        instance.slug = slug
        instance.save()

# @receiver(post_save, sender=StudentSubTopic)
# def student_subtopic_slug(sender, instance, created, **kwargs):
#     if created and not instance.slug:
#         slug = slugify(instance.topic.title)
#         instance.slug = slug
#         instance.save()


