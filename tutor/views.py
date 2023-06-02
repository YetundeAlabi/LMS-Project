from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.forms.models import modelform_factory
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
from django.apps import apps
from django.views.generic.edit import FormView

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

class TopicCreateView(TutorOwnerMixin, SuccessMessageMixin, FormView):
    template_name = 'courses/manage/module/formset.html'
    form_class = TopicFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Course.objects.get(id=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('course:course_list')

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
    
class SubTopicCreateUpdateView(TemplateResponseMixin, View):
    topic = None
    model = None
    obj = None
    template_name = 'tutor/subtopic.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='tutor',
            model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['course_tutor',
                                        'created_at',
                                        'updated_at'])
        return Form(*args, **kwargs)
  
    def dispatch(self, request, topic_id, model_name, id=None):
        self.topic = get_object_or_404(Topic, id=topic_id, course__course_tutor=request.user.tutor)
        self.model = self.get_model(model_name)
        # check if non-course_tutor can do the below
        if id:
            self.obj = get_object_or_404(self.model, id=id)
        return super().dispatch(request, topic_id, model_name, id)
    
    def get(self, request, topic_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})
    
    def post(self, request, topic_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course_tutor = request.user.tutor
            obj.save()
        
            if not id:
                SubTopic.objects.create(topic=self.topic, item=obj)
            return HttpResponseRedirect('course:topic_list', self.topic.id)
        return self.render_to_response({'form': form, 'object': self.obj})

class SubTopicDeleteView(View):
    
    def post(self, request, id):
        sub_topic = get_object_or_404(SubTopic, id=id, topic__course__course_tutor=request.user.tutor)
        topic = sub_topic.topic
        sub_topic.item.is_active = False
        sub_topic.save()
        return HttpResponseRedirect('course:course_list', topic.id)