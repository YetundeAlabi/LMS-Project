from django.contrib import admin
from .models import Course, Topic, SubTopic, File, Video, Text, Image

# Register your models here.

admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(SubTopic)
admin.site.register(File)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Text)
