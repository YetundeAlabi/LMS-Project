from django.shortcuts import render
from .models import StudentCourse, StudentTopic, StudentSubTopic
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

# Create your views here.


class StudentCourseListView(TemplateView):
    template_name = "course.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.students.first()
        context['student_track'] = student.track
        context["student_courses"] = StudentCourse.objects.filter(student=student)
        return context
    


class StudentTopicListView(View):
    def get(self, request, *args, **kwargs):
        student_course_slug=self.kwargs['student_course_slug']
        student_course=get_object_or_404(StudentCourse, slug=student_course_slug)
        student = self.request.user.students.first()
        Student_topics=StudentTopic.objects.filter(student_course__student=student , student_course=student_course)

        context ={
            'student_course_slug':student_course_slug,
            'student_topics':Student_topics
        }
        return render(self.request, 'topic.html', context=context)


class StudentSubtopicListView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        student_topic = get_object_or_404(StudentTopic, slug=student_topic_slug)
        student_subtopics = StudentSubTopic.objects.filter(
            student_topic__student_course__student=self.request.user.students.first(),
            student_topic=student_topic
        )
        context = {
            'student_course':student_topic.student_course,
            'student_topic': student_topic,
            'student_subtopics': student_subtopics
        }
        return render(self.request, 'subtopic.html', context=context)
    

class StudentSubtopicDetailView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        student_topic = get_object_or_404(StudentTopic, slug=student_topic_slug)
        student_subtopic_id = self.kwargs['student_subtopic_id']
        student_subtopic = get_object_or_404(StudentSubTopic, id=student_subtopic_id, student_topic=student_topic)
        student_subtopic.update_progress_level()
        student_subtopic.student_topic.update_progress_level()
        student_subtopic.student_topic.student_course.update_progress_level()
        
        context = {
            'student_topic': student_topic,
            'student_subtopic': student_subtopic
        }
        return render(self.request, 'subtopic_detail.html', context=context)
