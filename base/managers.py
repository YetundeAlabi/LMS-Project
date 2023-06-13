from django.db import models


class ActiveManager(models.Manager):
 def get_queryset(self):
    return super(ActiveManager, self).get_queryset().filter(is_deleted=False)


class DeletedManager(models.Manager):
 def get_queryset(self):
    return super(DeletedManager, self).get_queryset().filter(is_deleted=True)