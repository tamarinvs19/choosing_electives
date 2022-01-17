from django.db.models.signals import post_save, pre_save, pre_delete
from django.db.models import F, Max
from django.dispatch import receiver

from loguru import logger

from electives.models import StudentOnElective, ApplicationCounter, ElectiveKind


@receiver(pre_save, sender=StudentOnElective)
def pre_save_application(sender, instance, **kwargs):
    logger.info(f'PRE_SAVE:  {sender=}, {instance=}')
    changed_fields = instance.tracker.changed()
    if len(changed_fields) != 0:
        remove_application_from_counter(instance, changed_fields)
        add_application_to_counter(instance)


@receiver(pre_delete, sender=StudentOnElective)
def pre_delete_application(sender, instance, **kwargs):
    logger.info(f'PRE_DELETE:  {sender=}, {instance=}, {instance.tracker.changed()=}')
    remove_application_from_counter(instance, {})


def remove_application_from_counter(application, changed_fields):
    logger.info(f'REMOVE:  {application=}, {changed_fields=}')

    changed_fields = {
        key: value
        for key, value in changed_fields.items()
        if value is not None
    }

    kind_id = changed_fields.get('kind', application.kind.id)
    kind = ElectiveKind.objects.get(pk=kind_id)
    attached = changed_fields.get('attached', application.attached)

    only_one_similar_application = StudentOnElective.objects.filter(
        student=application.student,
        elective=application.elective,
        kind=kind,
        attached=attached,
    ).count() == 1

    if only_one_similar_application:
        counter, was_created = ApplicationCounter.objects.get_or_create(
            thematic=application.elective.thematic,
            elective=application.elective,
            language=kind.language,
            semester=kind.semester,
            attached=attached,
            credit_units=kind.credit_units,
        )
        counter.count_of_applications = max(counter.count_of_applications - 1, 0)
        counter.save()


def add_application_to_counter(application):
    logger.info(f'ADD:  {application=}')

    is_first_application = not StudentOnElective.objects.filter(
        student=application.student,
        elective=application.elective,
        kind=application.kind,
        attached=application.attached,
    ).exists()

    if is_first_application:
        counter, was_created = ApplicationCounter.objects.get_or_create(
            thematic=application.elective.thematic,
            elective=application.elective,
            language=application.kind.language,
            semester=application.kind.semester,
            attached=application.attached,
            credit_units=application.kind.credit_units,
        )
        counter.count_of_applications += 1
        counter.save()
