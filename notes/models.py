from django.db import models

from academic.models import Student, SubTopic
from users.models import CustomUser as User


class Assignment(models.Model):
    title = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class GradedAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.SET_NULL, blank=True, null=True
    )
    grade = models.FloatField()

    def __str__(self):
        return self.student.username


class Choice(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    question = models.CharField(max_length=200)
    choices = models.ManyToManyField(Choice)
    answer = models.ForeignKey(
        Choice, on_delete=models.CASCADE, related_name="answer", blank=True, null=True
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="questions",
        blank=True,
        null=True,
    )
    order = models.SmallIntegerField()

    def __str__(self):
        return self.question


class SpecificExplanations(models.Model):
    sub_topic = models.ForeignKey(
        SubTopic, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    examples = models.ManyToManyField(Question, blank=True)

    def __str__(self):
        return f"{self.name} {self.sub_topic}"


class Concept(models.Model):
    sub_topic = models.ForeignKey(
        SubTopic, on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    image = models.ImageField(
        verbose_name=None, upload_to="concept images", blank=True, null=True
    )
    list_of_explanations = models.ManyToManyField(SpecificExplanations, blank=True)

    def __str__(self):
        return f"{self.name} {self.sub_topic}"


class Note(models.Model):
    sub_topic = models.ForeignKey(
        SubTopic, on_delete=models.CASCADE, blank=True, null=True
    )
    notes = models.ManyToManyField(Concept, blank=True)

    def __str__(self):
        return f"{self.sub_topic}"
