from django.contrib import admin
from .models import Course, Topic, SubTopic
# Register your models here.

class TopicAdmin(admin.ModelAdmin):
    list_display= ('title', 'is_active')

admin.site.register(Course)
admin.site.register(Topic, TopicAdmin)
admin.site.register(SubTopic)
# admin.site.register(File)
# admin.site.register(Video)
# admin.site.register(Text)
# admin.site.register(SubtopicTest)
