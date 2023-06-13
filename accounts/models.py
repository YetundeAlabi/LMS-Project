from base import constants
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from lms_admin.models import Cohort, Track
from PIL import Image


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a  new user 
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """ create superuser """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class ActiveUserManager(models.Manager):
   def get_queryset(self) -> QuerySet:
       return super().get_queryset().filter(is_active=True)
    

class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model that supports using email instead of username"""
    
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    REQUIRED_FIELDS= []
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()
    active_objects = ActiveUserManager()

    def __str__(self):
        return self.email 
    
    @property
    def is_admin(self):
        return self.is_staff
    



class Student(models.Model):
    FEMALE = constants.FEMALE
    MALE = constants.MALE


    GENDER_CHOICES =(
        ("FEMALE", FEMALE),
        ("MALE", MALE),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, related_name='students', null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='accounts/media', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, related_name="students", null=True)

    
    def get_full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    
    def __str__(self):
        # return self.user.email
        return self.gender

    def get_absolute_url(self):
        return reverse('student_detail', args=[str(self.id)])


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="tutor")
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='accounts/media', blank=True)
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, related_name="tutors", null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.picture:
            img = Image.open(self.picture.path)
            if img.height > 100 or img.width > 100:
                new_img =(100, 100)
                img.thumbnail(new_img)
                img.save(self.picture.path)
                
        super().save(*args, **kwargs)