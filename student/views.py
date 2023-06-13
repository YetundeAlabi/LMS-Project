from django.shortcuts import render
from .models import StudentCourse, StudentTopic, StudentSubTopic
from django.views import View
from django.shortcuts import get_object_or_404

# Create your views here.


# class SubtopicListView(View):

#     def get(self):
#         topic_id=self.kwargs['topic_id']
#         topic=get_object_or_404()
#         StudentSubTopic.objects.filter(student_topic__student_course.student=self.request.user.student)
#     model = StudentSubTopic
#     template_name = 'student/subtopic_list.html'