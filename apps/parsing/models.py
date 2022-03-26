from django.db import models


class ConfigModel(models.Model):
    obj = None

    russian_url = models.URLField(
        default='https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021.html',
    )
    english_url = models.URLField(
        default='https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021_en.html',
    )
    google_form_url = models.URLField(
        default='https://docs.google.com/forms/d/12X4uaBPgNszp0DQ6juW8n9LP4b5jV4ro5TujiGngy-g/'
    )
    block_fall = models.BooleanField(default=False)

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = object.__new__(cls)
        return cls.obj
