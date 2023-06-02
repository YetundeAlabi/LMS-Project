from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.query import QuerySet
from django.urls import reverse


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


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model that supports using email instead of username"""
    # ADMIN = 0
    # TUTOR = 1
    # STUDENT = 2
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("TUTOR", "Tutor"),
        ("STUDENT", "Student")
    ]
    
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length= 50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()

    def __str__(self):
        return self.email 
    

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    last_login = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='accounts/media', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    # track = models.ForeignKey("Track", on_delete=models.SET_NULL, related_name="students", null=True)
    
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.user.email

    def get_absolute_url(self):
        return reverse('student_detail', args=[str(self.id)])



class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='accounts/media', blank=True)
    # track = models.ForeignKey("Track", on_delete=models.SET_NULL, related_name="Tutors", null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class ApprovedApplicantManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)
    

class Applicant(models.Model):
    GENDER_CHOICES =(
        ("FEMALE", "Female"),
        ("MALE", "Male"),
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    is_approved = models.BooleanField(default=False)
    objects = models.Manager()
    approved = ApprovedApplicantManager()
