from django.db import models
from django.db.models import Sum
from tutor.models import Student, Course, Topic, SubTopic, Track


# Create your models here.

class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        related_topics_count = self.student_topics.count()
        related_topics_progress_sum = self.student_topics.aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
        if related_topics_count > 0:
            average_progress = related_topics_progress_sum / related_topics_count
            self.progress_level = average_progress
            self.save()

    def __str__(self):
        return f' {self.course.title} for {self.student.user.first_name}'


class StudentTopic(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='student_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        related_sub_topics_count = self.student_subtopics.count()
        related_sub_topics_progress_sum = self.student_subtopics.aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
        if related_sub_topics_count > 0:
            average_progress = related_sub_topics_progress_sum / related_sub_topics_count
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

