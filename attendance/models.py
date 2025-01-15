from django.db import models
from django.conf import settings

from academic.models import Student
from users.models import CustomUser, Accountant
from academic.models import Teacher
import datetime


# Create your models here.
class AttendanceStatus(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text='"Present" will not be saved but may show as an option for teachers.',
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short code used on attendance reports. Example: 'A' might be the code for 'Absent'.",
    )
    excused = models.BooleanField(default=False)
    absent = models.BooleanField(
        default=False, help_text="Used for different types of absent statuses."
    )
    late = models.BooleanField(
        default=False, help_text="Used for tracking late statuses."
    )
    half = models.BooleanField(
        default=False,
        help_text="Indicates half-day attendance. Do not check absent, otherwise it will double count.",
    )

    class Meta:
        verbose_name_plural = "Attendance Statuses"

    def __str__(self):
        return self.name


class TeachersAttendance(models.Model):
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    teacher = models.ForeignKey(Teacher, blank=True, on_delete=models.CASCADE)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.ForeignKey(
        AttendanceStatus, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = (("teacher", "date", "status"),)
        ordering = ("-date", "teacher")

    def __str__(self):
        return f"{self.teacher} - {self.date} {self.status}"

    @property
    def edit(self):
        return f"Edit {self.teacher} - {self.date}"

    def save(self, *args, **kwargs):
        """Update for those who are late"""
        present, created = AttendanceStatus.objects.get_or_create(name="Present")

        # Check if the teacher is marked as "Present" and if they are late
        if (
            self.status == present
            and self.time_in
            and self.time_in >= datetime.time(7, 0, 0)
        ):
            self.status.late = True  # Mark status as late
        elif self.status != present:
            self.status.late = False  # Reset late if not present

        super(TeachersAttendance, self).save(*args, **kwargs)


class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, blank=True, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    ClassRoom = models.ForeignKey(
        "academic.ClassRoom", on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.ForeignKey(
        AttendanceStatus, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = (("student", "date", "status"),)
        ordering = ("-date", "student")

    def __str__(self):
        return f"{self.student.fname} - {self.date} {self.status}"

    @property
    def edit(self):
        return f"Edit {self.student.fname} - {self.date}"

    def save(self, *args, **kwargs):
        """Don't save if status is 'Present'"""
        present, created = AttendanceStatus.objects.get_or_create(name="Present")

        if self.status != present:
            super(StudentAttendance, self).save(*args, **kwargs)
        else:
            # Instead of deleting, just skip saving
            print(
                f"Attendance not saved for {self.student} on {self.date} because they are marked as 'Present'."
            )


class PeriodAttendance(models.Model):
    student = models.ForeignKey(Student, blank=True, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True, validators=settings.DATE_VALIDATORS)
    period = (
        models.IntegerField()
    )  # e.g., 1 for the first period, 2 for the second period, etc.
    status = models.ForeignKey(
        AttendanceStatus, blank=True, null=True, on_delete=models.CASCADE
    )
    reason_for_absence = models.CharField(max_length=500, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = (("student", "date", "period"),)
        ordering = ("date", "student", "period")

    def __str__(self):
        return f"{self.student.fname} - {self.date} Period {self.period} {self.status}"

    @property
    def edit(self):
        return f"Edit {self.student.fname} - {self.date} Period {self.period}"
