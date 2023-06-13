from django.db import models
from django.db.models import Sum
from tutor.models import Student, Tutor, Course, Topic, SubTopic, File, Video, Text, StudentCourse, StudentTopic, StudentSubTopic, Track


# Create your models here.

class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        topic_count = self.student_topics.count()
        topic_progress_sum = self.student_topics.aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
        if topic_count > 0:
            average_progress = topic_progress_sum / topic_count
            self.progress_level = average_progress
            self.save()

    def __str__(self):
        return f' {self.course.title} for {self.student.user.first_name}'


class StudentTopic(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='student_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    progress_level = models.FloatField(default=0.0)

    def update_progress_level(self):
        sub_topic_count = self.student_subtopics.count()
        sub_topic_progress_sum = self.student_subtopics.aggregate(Sum('progress_level')).get('progress_level__sum', 0.0)
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

