from django.contrib.auth.models import User


class Person(User):
    """Person model with sorting by the last name."""

    def __str__(self):
        if self.first_name and self.last_name:
            return '{0}. {1}'.format(self.first_name[0], self.last_name)
        else:
            return self.username

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'
        app_label = 'elective'
        proxy = True
        ordering = ('last_name', 'first_name')

