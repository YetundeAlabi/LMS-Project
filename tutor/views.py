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
from django.apps import apps


class OwnerMixin():
    def get_queryset(self):
        queryset= super().get_queryset()
        return queryset.filter(course_tutor=self.request.user.tutor)
       
class CourseListView(OwnerMixin, ListView):
    model = Course
    queryset = Course.active_objects.all()
    context_object_name = 'courses'

class CourseDetail(OwnerMixin, DetailView):
    model = Course
    context_object_name = 'course'
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    template_name = 'tutor/course_detail.html'

class CourseCreateView(OwnerMixin, CreateView):    
    model=Course
    form_class= CourseForm
    success_url = reverse_lazy('course:course_list')
    success_message= "Course Created Successfully" 
    template_name = 'tutor/course_create_update.html'

    def form_valid(self, form):
        form.instance.course_tutor=self.request.user
        return super().form_valid(form)

class CourseUpdateView(OwnerMixin, SuccessMessageMixin, UpdateView):    
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    success_message = "Course Updated Successfully"
    template_name ='tutor/course_create_update.html'
    form_class = CourseForm

class CourseDeleteView(OwnerMixin, DeleteView):
    model = Course
    slug_field= 'slug'
    slug_url_kwarg= 'course_slug'
    success_url = reverse_lazy('course:course_list')
    template_name = 'tutor/course_delete_confirm.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.info(request, 'Course deleted successfully')
        return HttpResponseRedirect(self.get_success_url())
    

class TopicList(LoginRequiredMixin, ListView):
    model=Topic
    queryset =Topic.active_objects.all()
    context_object_name = 'topics'
    template_name = 'tutor/topiclist.html'

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
    
class TopicUpdateView(SuccessMessageMixin, UpdateView):
    model = Topic
    # success_url = reverse_lazy('course: topic_list')
    success_message = 'Subtopic created successfully'
    template_name = 'tutor/topic_create_update.html'
    form_class = TopicForm


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