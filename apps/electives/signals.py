from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from loguru import logger

from apps.electives.models import StudentOnElective, ElectiveKind
from apps.electives.elective_statistic import Statistic


@receiver(pre_save, sender=StudentOnElective)
def pre_save_application(sender, instance, **kwargs):
    logger.info(f'PRE_SAVE:  {sender=}, {instance=}')
    changed_fields = instance.tracker.changed()
    if len(changed_fields) != 0:
        remove_application_from_counter(instance, changed_fields)
        add_application_to_counter(instance)


@receiver(pre_delete, sender=StudentOnElective)
def pre_delete_application(sender, instance, **kwargs):
    logger.info(f'PRE_DELETE:  {sender=}, {instance=}')
    remove_application_from_counter(instance, {})


def remove_application_from_counter(application: StudentOnElective, changed_fields):
    changed_fields = {
        key: value
        for key, value in changed_fields.items()
        if value is not None
    }

    kind_id = changed_fields.get('kind', application.kind.id)
    kind = ElectiveKind.objects.get(pk=kind_id)
    potential = changed_fields.get('potential', application.potential)

    statistic = Statistic()
    statistic.remove_student(
        application.elective,
        kind,
        application.student.id,
        potential,
    )


def add_application_to_counter(application: StudentOnElective):
    statistic = Statistic()
    statistic.add_student(
        application.elective,
        application.kind,
        application.student.id,
        application.potential,
    )

