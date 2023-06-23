from tutor.models import Course, Topic, SubTopic
from student.models import StudentCourse, StudentTopic, StudentSubTopic

def register_courses(student):
    courses_list = []
    related_topics_list = []

    student_track_courses = Course.objects.filter(track=student.track)
  
    for course in student_track_courses:
        courses_list.append(course)
    
    StudentCourse.objects.bulk_create(courses_list)

    # student_course = StudentCourse.objects.create(student=student, track=student.track, course=course)

    student_courses = StudentCourse.objects.filter(student=student)
  
    for student_course in student_courses:
        topics = Topic.objects.filter(course=student_course.course)
        for topic in topics:
            student_topic = StudentTopic.objects.create(student_course=student_course, topic=topic)
          
    student_topics = StudentTopic.objects.filter(student_course__student=student)
    for student_topic in student_topics:
        subtopics = SubTopic.objects.filter(topic=student_topic.topic)
        for subtopic in subtopics:
            student_subtopic = StudentSubTopic.objects.create(student_topic=student_topic, sub_topic=subtopic)
          