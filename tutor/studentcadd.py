from tutor.models import Student, Tutor, Course, Topic, SubTopic, File, Video, Text, StudentCourse, StudentTopic, StudentSubTopic, Track

student2 = Student.objects.get(id=2)
print(student2)

print(student2.track)

student_track_courses = Course.objects.filter(track=student2.track)
print(student_track_courses)

for course in student_track_courses:
    student1_course = StudentCourse.objects.create(student=student2, track=student2.track, course=course)
    print(student1_course)

student1_courses = StudentCourse.objects.filter(student=student2)
print(student1_courses)

for student_course in student1_courses:
    topics = Topic.objects.filter(course=student_course.course)
    for topic in topics:
        student_topic = StudentTopic.objects.create(student_course=student_course, topic=topic)
        print(student_topic)

student1_topics = StudentTopic.objects.filter(student_course__student=student2)
print(student1_topics)

for student_topic in student1_topics:
    subtopics = SubTopic.objects.filter(topic=student_topic.topic)
    for subtopic in subtopics:
        student_subtopic = StudentSubTopic.objects.create(student_topic=student_topic, sub_topic=subtopic)
        print(student_subtopic)