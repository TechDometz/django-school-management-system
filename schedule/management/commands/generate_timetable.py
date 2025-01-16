# timetable/management/commands/generate_timetable.py
from django.core.management.base import BaseCommand
from datetime import time, timedelta
from academic.models import AllocatedSubject
from schedule.models import Period
from administration.models import Term


class Command(BaseCommand):
    help = "Generate a timetable for the school learning days with a break after the fourth period."

    def handle(self, *args, **kwargs):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        period_duration = 40
        break_duration = 20
        periods_per_day = 8

        current_term = Term.objects.filter(is_current=True).first()
        if not current_term:
            self.stdout.write(self.style.ERROR("No current term set."))
            return

        allocated_subjects = AllocatedSubject.objects.filter(term=current_term)
        if not allocated_subjects.exists():
            self.stdout.write(
                self.style.WARNING("No AllocatedSubjects found for the current term.")
            )
            return

        for allocated_subject in allocated_subjects:
            weekly_limit = allocated_subject.weekly_periods
            max_daily_periods = allocated_subject.max_daily_periods
            classroom = allocated_subject.class_room
            subject = allocated_subject.subject
            teacher = allocated_subject.teacher

            day_periods = {day: 0 for day in days}

            for day in days:
                time_pointer = time(8, 0)
                consecutive_periods = 0

                for period_index in range(periods_per_day):
                    # Handle the break
                    if period_index == 4:
                        time_pointer = (
                            time_pointer.hour * 60
                            + time_pointer.minute
                            + break_duration
                        ) // 60, (time_pointer.minute + break_duration) % 60
                        time_pointer = time(*time_pointer)
                        continue

                    # Check weekly and daily limits
                    if (
                        day_periods[day] >= weekly_limit
                        or consecutive_periods >= max_daily_periods
                    ):
                        break

                    # Calculate end time
                    end_time_minutes = (
                        time_pointer.hour * 60 + time_pointer.minute + period_duration
                    )
                    end_time = time(end_time_minutes // 60, end_time_minutes % 60)

                    # Create the period
                    Period.objects.create(
                        day_of_week=day,
                        start_time=time_pointer,
                        end_time=end_time,
                        classroom=classroom,
                        subject=subject,
                        teacher=teacher,
                    )

                    day_periods[day] += 1
                    consecutive_periods += 1
                    time_pointer = end_time

        self.stdout.write(self.style.SUCCESS("Timetable generated successfully!"))
