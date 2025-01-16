import datetime
from django.db import models
from django.core.exceptions import ValidationError
from academic.models import Student, Teacher, ClassRoom, StudentClass, Subject
from administration.models import AcademicYear, Term


class GradeScale(models.Model):
    """Translate a numeric grade to some other scale.
    Example: Letter grade or 4.0 scale."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def get_rule(self, grade):
        if grade is None:
            return None
        rule = self.gradescalerule_set.filter(
            min_grade__lte=grade, max_grade__gte=grade
        ).first()
        if not rule:
            # Optionally log or raise a warning
            print(f"No rule found for grade: {grade}")
        return rule

    def to_letter(self, grade):
        rule = self.get_rule(grade)
        if rule:
            return rule.letter_grade
        return None  # Return None if no rule found

    def to_numeric(self, grade):
        rule = self.get_rule(grade)
        if rule:
            return rule.numeric_scale
        return None  # Return None if no rule found


class GradeScaleRule(models.Model):
    """One rule for a grade scale."""

    min_grade = models.DecimalField(max_digits=5, decimal_places=2)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=50, blank=True, null=True)
    numeric_scale = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    grade_scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("min_grade", "max_grade", "grade_scale")
        indexes = [
            models.Index(fields=["min_grade", "max_grade", "grade_scale"]),
        ]

    def __str__(self):
        return f"{self.min_grade}-{self.max_grade} {self.letter_grade} {self.numeric_scale}"

    def clean(self):
        """Ensure consistency between letter grade and numeric scale."""
        if not self.letter_grade and not self.numeric_scale:
            raise ValidationError(
                "Either a letter grade or numeric scale must be provided."
            )
        if self.letter_grade and self.numeric_scale is None:
            raise ValidationError(
                "If a letter grade is provided, numeric scale must also be provided."
            )
        if self.numeric_scale and self.letter_grade is None:
            raise ValidationError(
                "If a numeric scale is provided, a letter grade must also be provided."
            )

    def save(self, *args, **kwargs):
        if self.min_grade >= self.max_grade:
            raise ValidationError("min_grade must be less than max_grade.")
        super().save(*args, **kwargs)


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    gpa = models.FloatField(null=True)
    cat_gpa = models.FloatField(null=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.OneToOneField(Term, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.student)

    def clean(self):
        """Validate that GPA is within a valid range (0.0 - 4.0)."""
        if self.gpa is not None and (self.gpa < 0.0 or self.gpa > 4.0):
            raise ValidationError("GPA must be between 0.0 and 4.0.")
        if self.cat_gpa is not None and (self.cat_gpa < 0.0 or self.cat_gpa > 4.0):
            raise ValidationError("CAT GPA must be between 0.0 and 4.0.")


class ExaminationListHandler(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    ends_date = models.DateField()
    out_of = models.IntegerField()
    classrooms = models.ManyToManyField(ClassRoom, related_name="class_exams")
    comments = models.CharField(
        max_length=200, blank=True, null=True, help_text="Comments Regarding Exam"
    )
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        today = datetime.now().date()
        if today > self.ends_date:
            return "Done"
        elif self.start_date <= today <= self.ends_date:
            return "Ongoing"
        return "Coming Up"

    def __str__(self):
        return self.name

    def clean(self):
        """Ensure the start date is not later than the end date."""
        if self.start_date > self.ends_date:
            raise ValidationError("Start date cannot be later than end date.")
        super(ExaminationListHandler, self).clean()


class MarksManagement(models.Model):
    exam_name = models.ForeignKey(
        ExaminationListHandler, on_delete=models.CASCADE, related_name="exam_marks"
    )
    points_scored = models.FloatField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="subject_marks"
    )
    student = models.ForeignKey(
        StudentClass, on_delete=models.CASCADE, related_name="student_marks"
    )
    created_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="marks_entered"
    )
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name} - {self.student} - {self.points_scored}"

    def clean(self):
        """Validate points scored based on the exam's out_of value."""
        if self.points_scored < 0 or self.points_scored > self.exam_name.out_of:
            raise ValidationError(
                f"Points scored must be between 0 and {self.exam_name.out_of}."
            )
        super(MarksManagement, self).clean()
