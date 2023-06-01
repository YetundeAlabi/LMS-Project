from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser


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
    ADMIN = 0
    TUTOR = 1
    STUDENT = 2
    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TUTOR, "Tutor"),
        (STUDENT, "Student")
    ]
    
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=ADMIN)

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
    picture = models.ImageField(upload_to='accounts/media', blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.user.email


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='accounts/media', blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    