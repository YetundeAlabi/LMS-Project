from django.shortcuts import render
from .models import StudentCourse, StudentTopic, StudentSubTopic
from django.views import View
from django.shortcuts import get_object_or_404

# Create your views here.


class StudentCourseListView(View):
    def get(self, request, *args, **kwargs):
        student = self.request.user.students.first()
        student_courses = StudentCourse.objects.filter(student=student)
        context = {
            'student_courses':student_courses
        }
        return render(self.request, 'student/course.html', context=context)


class StudentTopicListView(View):
    def get(self, request, *args, **kwargs):
        student_course_slug = self.kwargs['student_course_slug']
        student_course = get_object_or_404(StudentCourse, slug=student_course_slug)
        student = self.request.user.student_set.first()
        student_topics = StudentTopic.objects.filter(student_course__student=student, student_course=student_course)

        context = {
            'student_course_slug': student_course_slug,
            'student_topics': student_topics,
        }
        return render(self.request, 'student/topic.html', context=context)



# class StudentSubtopicListView(View):
#     def get(self, request, *args, **kwargs):
#         student_topic_slug = self.kwargs['student_topic_slug']
#         student_topic = get_object_or_404(StudentTopic, slug=student_topic_slug)
#         student_subtopics = StudentSubTopic.objects.filter(
#             student_topic__student_course__student=self.request.user.student_set.first(),
#             student_topic=student_topic
#         )
#         context = {
#             'student_course':student_topic.student_course,
#             'student_topic': student_topic,
#             'student_subtopics': student_subtopics
#         }
#         return render(self.request, 'student/subtopic.html', context=context)
    

class StudentSubtopicDetailView(View):
    def get(self, request, *args, **kwargs):
        student_topic_slug = self.kwargs['student_topic_slug']
        student_topic = get_object_or_404(StudentTopic, slug=student_topic_slug)
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
