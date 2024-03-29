from accounts.models import Student
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render 
from django.views import View
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import (DetailView, TemplateView, UpdateView)

from .forms import ProfileUpdateForm
from .models import StudentCourse, StudentSubTopic, StudentTopic

# Create your views here.

class StudentProfileDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'student/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        students = Student.objects.filter(user=self.request.user)
        student = students.first()
        return student
    

class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = ProfileUpdateForm
    template_name = 'student/profile_update.html'

    def get_object(self, queryset=None):
        students = Student.objects.filter(user=self.request.user)
        student = students.first()
        return student

    def get_initial(self):
        initial = super().get_initial()
        student = self.get_object()
        initial['github_link'] = student.user.github_link
        initial['linkedin_link'] = student.user.linkedin_link
        initial['twitter_link']= student.user.twitter_link
        initial['picture'] = student.user.picture
        return initial

    def form_valid(self, form):
        student = self.get_object()
        user = student.user
        user.github_link = form.cleaned_data['github_link']
        user.linkedin_link = form.cleaned_data['linkedin_link']
        user.twitter_link = form.cleaned_data['twitter_link']
        user.picture = form.cleaned_data['picture']
        user.save()
        student.save()
        messages.success(self.request, "Student information updated successfully")
        return HttpResponseRedirect(reverse('student:profile_detail'))


class StudentActiveCourseListView(TemplateView):
    template_name = "student/course.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.students.first()
        context['student_track'] = student.track
        context["student_courses"] = StudentCourse.objects.filter(student=student, course__is_active=True, progress_level__lt=100)
        return context
    

class StudentCompletedCourseListView(TemplateView):
    template_name = "student/completed_courses.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.students.first()
        context['student_track'] = student.track
        context["student_courses"] = StudentCourse.objects.filter(student=student, progress_level=100)
        return context
 

class StudentTopicListView(View):
    def get(self, request, *args, **kwargs):
        student_course_slug = self.kwargs['student_course_slug']
        id = self.kwargs['pk']
        print(student_course_slug)
        student_course = get_object_or_404(StudentCourse, slug=student_course_slug, id=id)
        student = self.request.user.students.first()
        student_topics = StudentTopic.objects.filter(student_course__student=student, student_course=student_course)
       
        context ={
            'student_course_slug':student_course_slug,
            'student_topics':student_topics,
            'student_course':student_course
        }
        return render(self.request, 'student/student_topic_list.html', context=context)


class StudentSubtopicListView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        id = self.kwargs['pk']
        student_topic = get_object_or_404(StudentTopic, slug=student_topic_slug, id=id)
        student_subtopics = StudentSubTopic.objects.filter(
            student_topic__student_course__student=self.request.user.students.first(),
            student_topic=student_topic
        )
        context = {
            'student_course':student_topic.student_course,
            'student_topic': student_topic,
            'student_subtopics': student_subtopics
        }
        return render(self.request, 'student/subtopic.html', context=context)


class StudentSubtopicRedirectView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        id = self.kwargs['pk']
        print(id)
        student_course_slug = self.kwargs['student_course_slug']
        student=request.user.students.filter(is_current=True).get()
        print(student)
        student_topic = get_object_or_404(StudentTopic, student_course__student=student, slug=student_topic_slug)
        student_subtopic = StudentSubTopic.objects.filter(student_topic=student_topic)
        
        if student_subtopic.filter(progress_level=100.0).exists():
            student_subtopic = student_subtopic.filter(progress_level=100.0).last()
        else:
            student_subtopic = student_subtopic.filter(progress_level=0.0).first()
        if student_subtopic is not None:
            return redirect('student:student_subtopic_detail', student_course_slug=student_course_slug, pk=self.kwargs['pk'], student_topic_slug=student_topic_slug, student_topic_id=student_subtopic.student_topic.id, student_subtopic_id=student_subtopic.id)
        messages.info(request, 'No subtopic available')
        return redirect('student:topic_list', student_course_slug=student_course_slug, pk =self.kwargs['pk'])


class StudentSubtopicDetailView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        student=request.user.students.filter(is_current=True).get()
        
        student_topic = get_object_or_404(StudentTopic, id=self.kwargs['student_topic_id'])
        student_subtopic_id = self.kwargs['student_subtopic_id']

        # Get subtopic queryset to render sidebar
        student_subtopics = StudentSubTopic.objects.filter(
            student_topic__student_course__student=self.request.user.students.first(),
            student_topic=student_topic
        )

        # Get specific subtopic object 
        student_subtopic = get_object_or_404(StudentSubTopic, id=student_subtopic_id, student_topic=student_topic)

        #update progress level at all levels through the specific student_subtopic object above
        student_subtopic.update_progress_level()
        student_subtopic.student_topic.update_progress_level()
        student_subtopic.student_topic.student_course.update_progress_level()

        # Get the previous and next subtopics based on the current subtopic's position
        previous_subtopic = student_subtopics.filter(id__lt=student_subtopic_id).order_by('-id').first()
        next_subtopic = student_subtopics.filter(id__gt=student_subtopic_id).order_by('id').first()
        

        context = {
            'student_subtopics': student_subtopics,
            'student_topic': student_topic,
            'student_subtopic': student_subtopic,
            'student_course': student_subtopic.student_topic.student_course,
            'previous_subtopic': previous_subtopic,
            'next_subtopic': next_subtopic,
            'student_course_slug': self.kwargs['student_course_slug'],
            'student_topic_slug': student_topic_slug,   
        }

        return render(self.request, 'student/subtopic_detail.html', context=context)
