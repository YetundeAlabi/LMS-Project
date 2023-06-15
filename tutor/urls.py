from django.urls import path, include
from . import views


app_name= "course"
urlpatterns = [
    path('tutor_dashboard/', views.TutorDashboardView.as_view(), name='tutor_dashboard_view'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create_course', views.CourseAndTopicCreateView.as_view(), name='create_course'),
    path('courses/<slug:course_slug>', views.CourseDetail.as_view(), name='course_detail'),
    path('courses/<slug:course_slug>/update', views.CourseUpdateView.as_view(), name='update_course'),
    path('courses/<slug:course_slug>/delete', views.CourseDeleteView.as_view(), name='delete_course'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/update', views.TopicUpdateView.as_view(), name='update_topic'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/delete', views.TopicDeleteView.as_view(), name='delete_topic'),
    path('courses/<slug:course_slug>/topics/', views.TopicList.as_view(), name='topic_list'),
    path('course/<slug:course_slug>/topics/create', views.CreateTopicView.as_view(), name='create_topic'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('courses/<slug:course_slug>/topic/<uuid:pk>/subtopic/create', views.TopicUpdateView.as_view(), name='update_topic'),
    path('courses/<slug:course_slug>/topics/<uuid:pk>/subtopic/create', views.TopicUpdateView.as_view(), name='update_topic'),
    path('courses/<slug:course_slug>/topics/<uuid:pk>/subtopic/list', views.SubTopicList.as_view(), name='subtopic_list'),
    path('courses/<slug:course_slug>/topics', views.TopicList.as_view(), name='topic_list'),
    path('courses/<slug:course_slug>/topics/<int:id>/delete', views.TopicDeleteView.as_view(), name='create_topic'),
    path('subtopic/<int:id>/delete', views.SubTopicDeleteView.as_view(), name='delete_subtopic'),
    path('courses/<slug:course_slug>/topics/<uuid:topic_id>/subtopic/<str:model_name>/create', views.SubTopicCreateUpdateView.as_view(), name='create_subtopic'),
    path('courses/<slug:course_slug>/topics/<uuid:topic_id>/subtopic/<str:model_name>/<int:id>/update', views.SubTopicCreateUpdateView.as_view(), name='update_subtopic'),
    path('courses/<slug:course_slug>/topics/<uuid:topic_id>/subtopic/<str:model_name>/<int:id>/detail', views.SubTopicDetailView.as_view(), name='subtopic_detail'),

    path('track/students/', views.TrackStudentListView.as_view(), name='track_student_list'),
    path('track/students/<int:pk>/', views.TrackStudentDetailView.as_view(), name='track_student_detail'),
    path('topic/order/',  views.TopicOrderView.as_view(), name='topic_order'),
    path('subtopic/order/', views.SubTopicOrderView.as_view(), name='subtopic_order'),
    path('tutor/profile', views.TutorProfileView.as_view(), name='tutor_profile'),
    path('tutor/update/<int:pk>', views.TutorUpdateDetailsView.as_view(), name='tutor_update'),
    
]
    



 