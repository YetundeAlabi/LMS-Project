import uuid

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, AbstractUser
from django.db.models.query import QuerySet


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


class User(AbstractUser):
    """ Custom user model that supports using email instead of username"""

    class Role (models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TUTOR = "TUTOR", "Tutor"
        STUDENT = "STUDENT", "Student"
    
    base_role = Role.ADMIN 
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=Role.choices)

    is_student = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()

    def __str__(self):
        return self.email 
    
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        if not self.role or self.role == None:
            self.role = self.base_role
            self.is_admin = True
            return super().save(*args, **kwargs)


class StudentManager(BaseUserManager):
    
    def get_queryset(self, *args, **kwargs):
        queryset =  super().get_queryset(*args, **kwargs)
        return queryset.filter(role=User.Role.STUDENT)


class Student(User):
    base_role = User.Role.STUDENT
    objects = StudentManager()
    
    class Meta:
         db_table = 'student'

    def save(self, *args, **kwargs):
        self.role = User.Role.STUDENT
        self.is_student = True
        return super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return self.base_role
    

class TutorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results =  super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.TUTOR)


class Tutor(User):
    base_role = User.Role.TUTOR
    # objects = TutorManager()
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = User.Role.TUTOR
        self.is_tutor = True
        return super().save(*args, **kwargs)
    

