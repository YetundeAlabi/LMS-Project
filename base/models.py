from django.db import models

from .managers import ActiveManager, DeletedManager


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DeletableBaseModel(BaseModel):
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    deleted_objects = DeletedManager()

    class Meta:
        abstract = True
