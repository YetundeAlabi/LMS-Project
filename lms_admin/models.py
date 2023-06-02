from django.db import models


# Create your models here.

class Cohort(models.Model):
    year = models.PositiveIntegerField()
