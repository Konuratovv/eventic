from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import uuid

import random
import string

nb = dict(null=True, blank=True)


def generate_code(l: int):
    characters = string.ascii_letters + string.digits + string.punctuation
    code = ''.join(random.choice(characters) for i in range(l))
    return code


class UUIDMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField('ID', primary_key=True, default=uuid.uuid4, editable=False)


class GetOrNoneManager(models.Manager):
    """returns none if object doesn't exist else model instance"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None

    @sync_to_async
    def as_get_or_none(self, **kwargs):
        return self.get_or_none(**kwargs)


class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ['created_at']

    objects = models.Manager()
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
