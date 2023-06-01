from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Topic, SubTopic
from django.contrib import messages
from .forms import CourseForm, TopicFormSet, TopicForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import formset_factory
from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Student

class TutorOwnerMixin:
    def get_track(self):
        raise NotImplementedError("Subclasses of TutorOwnerMixin must implement the get_track() method.")
    def get_queryset(self):
        queryset = super().get_queryset()
        track = self.get_track()
        if self.request.user.tutor and self.request.user.tutor.track == track:
            return queryset.filter(course_tutor=self.request.user)

        return queryset.none()
    

class CourseListView(TutorOwnerMixin, ListView):
    model = Course
    queryset = Course.active_objects.all()
    context_object_name = 'courses'

    def get_track(self):
        course = self.get_object()
        return course.track


class CourseDetail(TutorOwnerMixin, DetailView):
    model = Course
    context_object_name = 'course'
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    template_name = 'tutor/course_detail.html'

    def get_track(self):
        course = self.get_object()
        return course.track

class CourseCreateView(TutorOwnerMixin, CreateView):    
    model=Course
    form_class= CourseForm
    success_url = reverse_lazy('course:course_list')
    success_message= "Course Created Successfully" 
    template_name = 'tutor/course_create_update.html'

    def get_track(self):
        course = self.get_object()
        return course.track

    def form_valid(self, form):
        form.instance.course_tutor=self.request.user
        return super().form_valid(form)
    
    

class CourseUpdateView(TutorOwnerMixin, SuccessMessageMixin, UpdateView):    
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    success_message = "Course Updated Successfully"
    template_name ='tutor/course_create_update.html'
    form_class = CourseForm

    def get_track(self):
        course = self.get_object()
        return course.track

class CourseDeleteView(TutorOwnerMixin, DeleteView):
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    template_name = 'tutor/course_delete_confirm.html'

    def get_track(self):
        course = self.get_object()
        return course.track

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.info(request, 'Course deleted successfully')
        return HttpResponseRedirect(self.get_success_url())
    

class TopicList(LoginRequiredMixin,TutorOwnerMixin, ListView):
    model=Topic
    queryset =Topic.active_objects.all()
    context_object_name = 'topics'
    template_name = 'tutor/topiclist.html'

    def get_track(self):
        topic = self.get_object()
        return topic.course.track

# class TopicCreateUpdateView(LoginRequiredMixin, CreateView):
#     template_name = 'tutor/topic_create_update.html'
#     form_class = TopicFormSet
#     model = Course
#     course = None

#     def dispatch(self, request, course_slug):
#         self.course = get_object_or_404(Course, slug=course_slug, course_tutor=self.request.user.tutor)
#         return super().dispatch(request, course_slug)
    
#     def get_formset(self, data=None):
#         return TopicFormSet(instance=self.course, data=data)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['formset'] = self.form_class(queryset=Topic.objects.none(), instance=self.course)
#         return data

#     def form_valid(self, form):
#         formset = self.get_formset(data=self.request.POST)
#         if formset.is_valid():
#             formset.save()
#             return HttpResponse('Topic created')
#         else:
#             return self.form_invalid(form)
    
#     def post(self, request, *args, **kwargs):
#         form = self.get_form()
#         formset = self.get_formset(data=request.POST)
#         if form.is_valid() and formset.is_valid():
#             self.object = form.save(commit=False)
#             self.object.course = self.course
#             self.object.save()
#             formset.instance = self.object
#             formset.save()
#             return HttpResponse('Topic created')
#         else:
#             return self.form_invalid(form)

# class TopicCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'tutor/topic_create_update.html'
#     form_class = TopicFormSet
#     model = Course

#     def dispatch(self, request, course_slug):
#         self.course = get_object_or_404(Course, slug=course_slug, course_tutor=self.request.user.tutor)
#         return super().dispatch(request, course_slug)

#     def form_valid(self, form):
#         form.instance.course = self.course
#         form.save()
#         return HttpResponse('Topic created')
    

# class TopicUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = 'tutor/topic_create_update.html'
#     form_class = TopicFormSet
#     model = Course

#     def dispatch(self, request, course_slug):
#         self.course = get_object_or_404(Course, slug=course_slug, course_tutor=self.request.user.tutor)
#         return super().dispatch(request, course_slug)

#     def form_valid(self, form):
#         form.instance.course = self.course
#         form.save()
#         return HttpResponse('Topic updated')
    

# class TopicCreateUpdateView(TemplateResponseMixin, View):
#     template_name = 'tutor/topic_create_update.html'
#     get_formset = TopicFormSet

#     def get_formset(self, data=None):
#         return TopicFormSet(instance=self.course, data=data)
    
#     def dispatch(self, request, course_slug):
#         self.course = get_object_or_404(Course, slug=course_slug, course_tutor=self.request.user.tutor)
#         return super().dispatch(request, course_slug)
    
#     def get(self, request, *args, **kwargs):
#         formset = self.get_formset()
#         return self.render_to_response({'course': self.course, 'formset': formset})
    
#     def post(self, request, *args, **kwargs):
#         formset = self.get_formset(data=request.POST)
#         if formset.is_valid():
#             formset.save()
#             return HttpResponse('Topic created')
#             # return HttpResponseRedirect('manage_course_list')
#         return self.render_to_response({'course': self.course,'formset': formset})



# class TopicCreateView(SuccessMessageMixin, CreateView):
#     model = Topic
#     # success_url = reverse_lazy('course: subtopic_list')
#     success_message = 'Subtopic created successfully'
#     template_name = 'tutor/topic_create_update.html'
#     # form_class = TopicForm
    
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         form.formsets = TopicFormSet(form_kwargs=self.get_form_kwargs())
#         return form


#     def form_valid(self, form):
#         course_slug=self.kwargs['slug']
#         course= get_object_or_404(Course, slug=course_slug)
#         form.instance.course=course
#         return super().form_valid(form)
    

class TopicUpdateView(TutorOwnerMixin, SuccessMessageMixin, UpdateView):
    model = Topic
    success_url = reverse_lazy('course:topic_list')
    success_message = 'Subtopic created successfully'
    template_name = 'tutor/update_topic_form.html'
    form_class = TopicForm
    pk_url_kwarg='pk'

    def get_track(self):
        topic = self.get_object()
        return topic.course.track

    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse_lazy('course:topic_list', kwargs={'course_slug': course_slug})
    

class TopicDeleteView(LoginRequiredMixin, TutorOwnerMixin, UpdateView):
    model = Topic
    pk_url_kwarg ='pk'
    template_name = 'tutor/course_delete_confirm.html'
    fields=[]

    def get_track(self):
        topic = self.get_object()
        return topic.course.track


    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.info(request, 'Course deleted successfully')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse_lazy('course:topic_list', kwargs={'course_slug': course_slug})
    

class TrackStudentListView(LoginRequiredMixin, TutorOwnerMixin, ListView):
    model = Student
    context_object_name = 'students'

    def get_queryset(self):
        track = self.request.user.tutor.track
        return super().get_queryset().filter(track=track)
    



# class TopicDeleteView(OwnerMixin, DeleteView):
#     model = Topic
#     # slug_field= 'slug'
#     # slug_url_kwarg= 'course_slug'
#     success_url = reverse_lazy('course:course_list')
#     template_name = 'tutor/course_delete_confirm.html'

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         self.object.is_active = False
#         self.object.save()
#         messages.info(request, 'Topic deleted successfully')
#         return HttpResponseRedirect(self.get_success_url())
    

