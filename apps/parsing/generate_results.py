from apps.electives.models import StudentOnElective
from apps.users.models import Person


def generate_application_layers(person: Person) -> list[list[StudentOnElective]]:
    applications = StudentOnElective.objects.filter(
        student=person,
        potential=False,
    )
