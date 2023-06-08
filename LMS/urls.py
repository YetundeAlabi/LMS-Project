"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import HomePage
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    
    path('home/', HomePage.as_view(), name="home_page"),
    path('', include('accounts.urls', namespace="accounts")),
    path('admin/', admin.site.urls), 
    path('tutor/', include('tutor.urls', namespace="course")),
    path('LMS/admin/', include('lms_admin.urls', namespace="lms_admin")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
