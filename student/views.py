from django.shortcuts import render
from .models import StudentCourse, StudentTopic, StudentSubTopic
from django.views import View
from django.shortcuts import get_object_or_404

# Create your views here.


class StudentSubtopicListView(View):
    def get(self, request, *args, **kwargs):
        student_topic_id = self.kwargs['student_topic_id']
        student_topic = get_object_or_404(StudentTopic, id=student_topic_id)
        student_subtopics = StudentSubTopic.objects.filter(
            student_topic__student_course__student=request.user.student,
            student_topic__topic=student_topic
        )
        context = {
            'student_topic': student_topic,
            'student_subtopics': student_subtopics
        }
        return render(self.request, 'student/subtopic.html', context=context)
    

class StudentSubtopicDetailView(View):
    def get(self, request, *args, **kwargs):
        student_topic_id = self.kwargs['student_topic_id']
        student_topic = get_object_or_404(StudentTopic, id=student_topic_id)
        student_subtopic_id = self.kwargs['student_subtopic_id']
        student_subtopic = get_object_or_404(StudentSubTopic, id=student_subtopic_id, student_topic=student_topic)
        student_subtopic.update_progress_level()
        student_topic.update_progress_level()
        student_topic.student_course.update_progress_level()
        
        context = {
            'student_topic': student_topic,
            'student_subtopic': student_subtopic
        }
        return render(self.request, 'student/subtopic.html', context=context)
