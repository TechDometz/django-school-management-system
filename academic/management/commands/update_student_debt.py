from django.core.management.base import BaseCommand
from academic.models import Student
from administration.models import Term, AcademicYear
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Update student debt at the start of each term and carry forward unpaid debt to the new academic year."

    def handle(self, *args, **kwargs):
        # Get the current date
        today = now().date()

        # Get the current academic year and term
        current_term = Term.objects.filter(
            start_date__lte=today, end_date__gte=today
        ).first()
        current_year = AcademicYear.objects.filter(current=True).first()

        if not current_term:
            self.stdout.write("No active term found for today.")
            return

        # Update debts for the current term
        students = Student.objects.all()
        for student in students:
            if current_term.academic_year == current_year:
                student.update_debt_for_term(current_term)
            else:
                student.carry_forward_debt_to_new_academic_year()

        self.stdout.write(f"Debts updated for term: {current_term.name}.")
