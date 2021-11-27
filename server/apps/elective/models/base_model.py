from django.db import models


class TimedModel(models.Model):
    """Abstract model with `created_at` and `updated_at` fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True
        app_label = 'elective'
