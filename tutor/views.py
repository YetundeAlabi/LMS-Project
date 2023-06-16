from typing import Any, Dict
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms.models import modelform_factory
from django.forms.widgets import TextInput, Textarea
from django.http import Http404
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View, ContextMixin, TemplateView
from accounts.models import Student, Tutor
from .forms import TutorUpdateForm
from .forms import CourseForm, TopicForm, TopicFormSet
from .models import Course, Topic, SubTopic
from accounts.models import User
from django.views.generic.base import TemplateResponseMixin
from .forms import TutorUpdateForm
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.views import View


class TutorUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tutor
    
class TutorDashboardView(TutorUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tutor= self.request.user.tutor
        students= Student.objects.filter(track=tutor.track)
        courses = Course.objects.filter(track=tutor.track)
        courses_list = [course.title for course in courses]
        courses_topic_count = [course.topic_set.count() for course in courses]
        
        context = {
            'tutor':tutor,
            'students':students,
            'courses': courses,
            'courses_list': courses_list,
            'courses_topic_count': courses_topic_count,
        }
        return render (self.request, 'tutor/tutor_dashboard.html', context=context)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.filter(course=self.get_object())
        return context
   
   
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
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class CreateTopicView(TutorUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Topic
    form_class = TopicForm
    success_message = 'Topic created successfully'
    template_name = 'tutor/topic_form.html'


    def form_valid(self, form):
        course_slug = self.kwargs['course_slug']
        course = get_object_or_404(Course, slug=course_slug)
        title = form.cleaned_data.get('title')
        if Topic.objects.filter(course=course, title=title).exists():
            messages.error(self.request, 'Topic title under the same course already exists')
            return self.render_to_response(self.get_context_data(form=form))
        instance = form.save(commit=False)
        instance.course = course
        return super().form_valid(form)

    def get_success_url(self):
        course_slug = self.kwargs['course_slug']
        return reverse('course:topic_list', kwargs={'course_slug': course_slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']
        return context


class TopicDetailView(TutorUserRequiredMixin, DetailView):
    model = Topic
    template_name='tutor'
    context_object_name = 'topic'
    template_name = 'tutor/topic_detail.html'


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
        track = self.request.user.tutor.track
        return super().get_queryset().filter(course__track=track, course__slug=course_slug)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(*kwargs)
        course_slug=self.kwargs['course_slug']
        context['course_slug']=course_slug
        context['course'] = get_object_or_404(Course, slug=course_slug)
        return context
    

class TopicUpdateView(TutorUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Topic
    success_message = 'Subtopic updated successfully'
    template_name = 'tutor/update_topic_form.html'
    form_class = TopicForm
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.course.course_tutor != self.request.user.tutor:
            messages.error(self.request, "You cannot update topics under another tutor's course")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        course_slug = self.object.course.slug
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
        return HttpResponseRedirect(reverse('course:track_student_detail', kwargs={'pk':student.id}))

class SubTopicCreateUpdateView(TemplateResponseMixin, View):
    topic = None
    model = None
    obj = None
    template_name = 'tutor/subtopic.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'file']:
            return apps.get_model(app_label='tutor', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=[
            'created_at',
            'updated_at',
            'is_active',
        ])

        for field_name, field in Form.base_fields.items():
            if isinstance(field.widget, TextInput) or isinstance(field.widget, Textarea):
                field.widget.attrs['class'] = 'form-control form-control-lg'
        return Form(*args, **kwargs)

    def dispatch(self, request, course_slug, topic_id, model_name, id=None):
        self.topic = get_object_or_404(
            Topic,
            id=topic_id,
            course__slug=course_slug,
            course__course_tutor=request.user.tutor
        )
        self.model = self.get_model(model_name)
        if id:
            try:
                self.obj = self.model.objects.get(id=id)
            except self.model.DoesNotExist:
                raise Http404
        return super().dispatch(request, course_slug, topic_id, model_name, id)

    def get(self, request, course_slug, topic_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, course_slug, topic_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            if id:
                obj = form.save(commit=False)
                if 'file' in request.FILES:
                    obj.file = request.FILES['file']
                obj.save()

            if not id:
                obj = form.save(commit=False)
                if 'file' in request.FILES:
                    obj.file = request.FILES['file']
                obj.save()

                subtopic = SubTopic(topic=self.topic, item=obj)
                subtopic.title = form.cleaned_data['title']
                subtopic.description = form.cleaned_data['description']
                subtopic.save()
            return HttpResponseRedirect(reverse('course:subtopic_list', kwargs={'course_slug': self.topic.course.slug, 'pk': topic_id}))
        return self.render_to_response({'form': form, 'object': self.obj})


class SubTopicDeleteView(View):
    
    def get(self, request, *args, **kwargs):
        subtopic=get_object_or_404(SubTopic, id=self.kwargs['id'])
        return render(request, 'tutor/course_delete_confirm.html', {'subtopic': subtopic})

    def post(self, request, id):
        sub_topic = get_object_or_404(SubTopic, id=id, topic__course__course_tutor=request.user.tutor)
        sub_topic.is_active = False
        sub_topic.save()
        return HttpResponseRedirect(reverse('course:subtopic_list', kwargs={'course_slug': sub_topic.topic.course.slug, 'pk':sub_topic.topic.id}))
    
    
class SubTopicList(TutorUserRequiredMixin, ListView):
    model=SubTopic
    queryset =SubTopic.active_objects.all()
    context_object_name = 'subtopics'
    template_name = 'tutor/subtopic_list.html'

    def get_queryset(self):
        topic_id=self.kwargs['pk']
        course_slug=self.kwargs['course_slug']
        return super().get_queryset().filter(topic=get_object_or_404(Topic, id=topic_id))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = self.kwargs['pk']
        context['topic'] = get_object_or_404(Topic, id=topic_id)
        return context
    

class SubTopicDetailView(TutorUserRequiredMixin, DetailView):
    model = SubTopic
    context_object_name='subtopic'
    template_name = 'tutor/subtopic_detail.html'
    pk_url_kwarg ='id'


class TopicOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Topic.active_objects.filter(id=id, course__course_tutor=request.user.tutor).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class SubTopicOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            print(self.request_json.items())
            print('id', id)
            print('order', order)
            SubTopic.active_objects.filter(id=id, topic__course__course_tutor=request.user.tutor) \
                                                                    .update(order=order)
        return self.render_json_response({'saved': 'OK'})
  

class TutorProfileView(TemplateView):
    template_name = 'tutor/tutor_profile.html'


class TutorUpdateView(UpdateView):
    model = Tutor
    form_class = TutorUpdateForm
    template_name = 'tutor/tutor_update.html'
    success_url = reverse_lazy('course:tutor_profile')

    def form_valid(self, form):
        tutor = form.instance
        tutor.user.first_name = form.cleaned_data['first_name']
        tutor.user.last_name = form.cleaned_data['last_name']
        tutor.picture = form.cleaned_data['picture']
        tutor.user.save()
        return super().form_valid(form)