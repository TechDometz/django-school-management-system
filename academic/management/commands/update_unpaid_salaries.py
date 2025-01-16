from django.core.management.base import BaseCommand
from users.models import Accountant
from academic.models import Teacher
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Update unpaid salaries for all teachers and accountants."

    def handle(self, *args, **kwargs):
        # Get the current date
        today = now().date()

        # Check if it's the start of a new month
        if today.day == 1:
            # Update unpaid salary for all teachers and accountants
            teachers = Teacher.objects.all()
            accountants = Accountant.objects.all()

            for teacher in teachers:
                teacher.update_unpaid_salary()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated unpaid salary for {teacher.first_name} {teacher.last_name}."
                    )
                )

            for accountant in accountants:
                accountant.update_unpaid_salary()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated unpaid salary for {accountant.first_name} {accountant.last_name}."
                    )
                )

            self.stdout.write(
                self.style.SUCCESS("All unpaid salaries have been updated.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "It's not the start of the month, no updates were made."
                )
            )
