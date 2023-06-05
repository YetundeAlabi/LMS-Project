from django.apps import apps
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.views.generic.base import View
from django.views.generic.base import TemplateResponseMixin
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms.models import modelform_factory
from django.shortcuts import redirect
from .models import Course, Topic, SubTopic
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
    success_url = reverse_lazy('course:course_list')

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
            topic_formset = topic_formset.save(commit=False)
            for instance in topic_formset:
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


class CourseDeleteView(TutorUserRequiredMixin, View):
    def get(self, request, course_slug):
        course= get_object_or_404(Course, slug=course_slug)
        return render(request, 'tutor/course_delete_confirm.html', {'course': course})

    def post(self, request, course_slug):
        course= get_object_or_404(Course, slug=course_slug)
        if course.course_tutor != self.request.user.tutor:
            messages.error(request, "You cannot delete another tutor's course")
            return redirect('course:course_list')    
        course.is_active = False
        course.save()
        messages.info(request, 'Course deleted successfully')
        return redirect('course:course_list')


class TopicList(TutorUserRequiredMixin, ListView):
    model=Topic
    queryset =Topic.active_objects.all()
    context_object_name = 'topics'
    template_name = 'tutor/topiclist.html'

    def get_queryset(self):
        course_slug=self.kwargs['course_slug']
        print(course_slug)
        track = self.request.user.tutor.track
        return super().get_queryset().filter(course__track=track, course__slug=course_slug)
    

class TopicUpdateView(TutorUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Topic
    success_url = reverse_lazy('course:topic_list')
    success_message = 'Subtopic created successfully'
    template_name = 'tutor/update_topic_form.html'
    form_class = TopicForm
    pk_url_kwarg='pk'

    def dispatch(self, request, *args, **kwargs):
        topic= self.get_object()
        if topic.course.course_tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot update topics under another tutor's course")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse_lazy('course:topic_list', kwargs={'course_slug': course_slug})


class TopicDeleteView(TutorUserRequiredMixin, View):
    
    def get_object(self):
        pk = self.kwargs['pk']
        return get_object_or_404(Topic, id=pk)
    
    def get(self, request, *args, **kwargs):
        topic = self.get_object()
        return render(request, 'tutor/course_delete_confirm.html', {'topic': topic})

    def dispatch(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.course.course_tutor != self.request.user.tutor:
            messages.error(request, "You cannot update topics under another tutor's course")
            return redirect('course:topic_list', course_slug=topic.course.slug)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        topic.is_active = False
        topic.save()
        messages.info(request, 'Topic deleted successfully')
        return redirect('course:topic_list', course_slug=topic.course.slug)

    
class TrackStudentListView(TutorUserRequiredMixin, ListView):
    model = Student
    context_object_name = 'students'
    template_name = 'tutor/track_student_list.html'

    def get_queryset(self):
        track = self.request.user.tutor.track
        return super().get_queryset().filter(track=track)
    

class TrackStudentDetailView(TutorUserRequiredMixin, DetailView):
    model = Student
    template_name = 'tutor/track_student_detail.html'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        student = self.get_object()
        if self.request.user.tutor.track != student.track:
            messages.error(request, 'You cannot view the details of students in other tracks')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        student_suspension_status = student.is_suspended
        student.is_suspended = not student_suspension_status
        student.save()
        messages.success(request, "Student suspension status has been changed successfully.")
        return HttpResponseRedirect(reverse('course:track_student_detail', kwargs={'pk': student.pk}))


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
                                        'updated_at',
                                        'is_active'])
        return Form(*args, **kwargs)
  
    def dispatch(self, request, topic_id, model_name, id=None):
        self.topic = get_object_or_404(Topic, id=topic_id, course__course_tutor=request.user.tutor)
        self.model = self.get_model(model_name)
        
        if id:
            self.obj = get_object_or_404(self.model, id=id, tutor=request.user.tutor)
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
    
    

