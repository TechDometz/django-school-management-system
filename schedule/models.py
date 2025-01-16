from django.db import models

from academic.models import ClassRoom, Teacher, AllocatedSubject


class Period(models.Model):
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
        ],
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(AllocatedSubject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("day_of_week", "start_time", "classroom")

    def __str__(self):
        return f"{self.classroom} - {self.subject} ({self.day_of_week} {self.start_time}-{self.end_time})"
