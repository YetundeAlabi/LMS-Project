from django.shortcuts import render
from .models import StudentCourse, StudentTopic, StudentSubTopic
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
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

class StudentTopicView(TemplateView):
    template_name = 'student/student_course.html'

class StudentTopicList(LoginRequiredMixin, ListView):
    model= StudentTopic
    queryset = StudentTopic.objects.all()
    context_object_name = 'student_topics'
    template_name = 'student/student_course.html'

    def get_queryset(self):
        student_course_slug=self.kwargs['slug']
        track = self.request.user.track
        return super().get_queryset().filter(student_course__track=track, slug=student_course_slug)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(*kwargs)
        student_course_slug=self.kwargs['slug']
        context['slug']= student_course_slug
        context['student_course'] = get_object_or_404(StudentCourse, slug=student_course_slug)
        return context