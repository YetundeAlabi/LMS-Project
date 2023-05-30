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
    

class User(AbstractUser):
    """ Custom user model that supports using email instead of username"""
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("TUTOR", "Tutor"),
        ("STUDENT", "Student")
    ]
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="ADMIN")

    USERNAME_FIELD = "email"
    objects = MyUserManager()

    def __str__(self):
        return self.email 
    

class Student(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_verify = models.BooleanField(default=False)
    # add profile picture 
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    

# create tutor and admin class
# change auth user model in settings