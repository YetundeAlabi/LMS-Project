from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import Course, Topic
from .forms import CourseForm, TopicForm, TopicFormSet
from accounts.models import Student



class TutorUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tutor
    

class CourseListView(TutorUserRequiredMixin, ListView):
    model = Course
    queryset = Course.active_objects.all()
    context_object_name = 'courses'

    def get_queryset(self):
        track = self.request.user.tutor.track
        return super().get_queryset().filter(track=track)


class CourseDetail(TutorUserRequiredMixin, DetailView):
    model = Course
    context_object_name = 'course'
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    template_name = 'tutor/course_detail.html'
   

class CourseAndTopicCreateView(TutorUserRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'tutor/course_create_update.html'
    success_url = reverse_lazy('course_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['topic_formset'] = TopicFormSet(self.request.POST)
        else:
            data['topic_formset'] = TopicFormSet()
        return data

    def form_valid(self, form):
        form.instance.course_tutor = self.request.user.tutor
        form.instance.track = self.request.user.tutor.track
        context = self.get_context_data()
        topic_formset = context['topic_formset']
        if topic_formset.is_valid():
            course = form.save()
            instances = topic_formset.save(commit=False)
            for instance in instances:
                instance.course = course
                instance.save()
            for obj in topic_formset.deleted_objects:
                obj.delete()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)



class CourseUpdateView(TutorUserRequiredMixin, SuccessMessageMixin, UpdateView):    
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    success_message = "Course Updated Successfully"
    template_name ='tutor/course_create_update.html'
    form_class = CourseForm

    def dispatch(self, request, *args, **kwargs):
        course= self.get_object()
        if course.course_tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot update another tutor's course")
        return super().dispatch(request, *args, **kwargs)


class CourseDeleteView(TutorUserRequiredMixin, UpdateView):
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    template_name = 'tutor/course_delete_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        course= self.get_object()
        if course.course_tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot delete another tutor's course")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        course.is_active = False
        course.save()
        messages.info(request, 'Course deleted successfully')
        return HttpResponseRedirect(self.get_success_url())  


class TopicList(TutorUserRequiredMixin, ListView):
    model=Topic
    queryset =Topic.active_objects.all()
    context_object_name = 'topics'
    template_name = 'tutor/topiclist.html'

    def get_queryset(self):
        track = self.request.user.tutor.track
        return super().get_queryset().filter(course__track=track)
    

class TopicUpdateView(TutorUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Topic
    success_url = reverse_lazy('course:topic_list')
    success_message = 'Subtopic created successfully'
    template_name = 'tutor/update_topic_form.html'
    form_class = TopicForm
    pk_url_kwarg='pk'

    def dispatch(self, request, *args, **kwargs):
        topic= self.get_object()
        if topic.course.tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot update topics under another tutor's course")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse_lazy('course:topic_list', kwargs={'course_slug': course_slug})
    

class TopicDeleteView(TutorUserRequiredMixin, View):
    model = Topic
    pk_url_kwarg ='pk'
    template_name = 'tutor/course_delete_confirm.html'
    fields=[]

    def dispatch(self, request, *args, **kwargs):
        topic= self.get_object()
        if topic.course.tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot update topics under another tutor's course")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        topic.is_active = False
        topic.save()
        messages.info(request, 'Topic deleted successfully')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse_lazy('course:topic_list', kwargs={'course_slug': course_slug})
    

class TrackStudentListView(TutorUserRequiredMixin, ListView):
    model = Student
    context_object_name = 'students'

    def get_queryset(self):
        track = self.request.user.tutor.track
        return super().get_queryset().filter(track=track)
    

class SuspendStudent(TutorUserRequiredMixin, View):
    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        return render(request, 'tutor/suspend_student.html', {'student': student})
    
    def dispatch(self, request, student_id, *args, **kwargs):
        student = get_object_or_404(Student, id=student_id)
        if self.request.user.tutor.track != student.track:
            messages.error(request, "You can only suspend students from your own track.")
            return HttpResponseRedirect(reverse('student_detail', kwargs={'student_id': student_id}))
        return super().dispatch(request, student_id, *args, **kwargs)
    
    def post(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        student.is_suspended = True
        student.save()
        messages.success(request, "Student suspended successfully.")
        return HttpResponseRedirect(reverse('student_detail', kwargs={'student_id': student_id}))
    

