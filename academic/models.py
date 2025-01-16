from django.db import models, transaction
from django.db.models import F
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils import timezone
from users.models import CustomUser
from administration.models import AcademicYear, Term
from .validators import *
from administration.common_objs import *


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order_rank = models.IntegerField(
        blank=True, null=True, help_text="Rank for course reports"
    )

    class Meta:
        ordering = ("order_rank", "name")

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject_code = models.CharField(max_length=10, blank=True, null=True, unique=True)
    is_selectable = models.BooleanField(
        default=False, help_text="Select if subject is optional"
    )
    graded = models.BooleanField(default=True, help_text="Teachers can submit grades")
    description = models.CharField(max_length=255, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.name


class Teacher(models.Model):
    username = models.CharField(unique=True, max_length=250, blank=True)
    first_name = models.CharField(max_length=300, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=300, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, blank=True)
    email = models.EmailField(blank=True, null=True)
    empId = models.CharField(max_length=8, unique=True, null=True, blank=True)
    tin_number = models.CharField(max_length=9, blank=True, null=True)
    nssf_number = models.CharField(max_length=9, blank=True, null=True)
    short_name = models.CharField(max_length=3, blank=True, null=True, unique=True)
    isTeacher = models.BooleanField(default=True)
    salary = models.IntegerField(blank=True, null=True)
    unpaid_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subject_specialization = models.ManyToManyField(Subject, blank=True)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=150, blank=True)
    alt_email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="Employee_images", blank=True, null=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def deleted(self):
        return self.inactive

    def save(self, *args, **kwargs):
        # Generate unique username
        if not self.username:
            self.username = f"{self.first_name.lower()}{self.last_name.lower()}{get_random_string(4)}"

        # Create corresponding user
        super().save(*args, **kwargs)
        user, created = CustomUser.objects.get_or_create(
            email=self.email,
            defaults={
                "first_name": self.first_name,
                "last_name": self.last_name,
                "is_teacher": self.isTeacher,
            },
        )
        if created:
            default_password = f"Complex.{self.empId[-4:] if self.empId and len(self.empId) >= 4 else '0000'}"
            user.set_password(default_password)
            user.save()

            # Add to "teacher" group
            group, _ = Group.objects.get_or_create(name="teacher")
            user.groups.add(group)

            # Optionally send email (integrate email backend here)

    def update_unpaid_salary(self):
        # Update unpaid salary at the start of each month
        current_month = timezone.now().month
        if self.unpaid_salary > 0:
            self.unpaid_salary += self.salary  # Add salary amount to unpaid salary
        else:
            self.unpaid_salary = (
                self.salary
            )  # If unpaid salary is 0, set the first month's salary
        self.save()


class ClassLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Class Level")
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class GradeLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Grade Level")
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class ClassYear(models.Model):
    year = models.CharField(max_length=100, unique=True, help_text="Example 2020")
    full_name = models.CharField(
        max_length=255, help_text="Example Class of 2020", blank=True
    )

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"Class of {self.year}"
        super().save(*args, **kwargs)


class ReasonLeft(models.Model):
    reason = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.reason


class Stream(models.Model):
    name = models.CharField(max_length=50, validators=[stream_validator])

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, blank=True, related_name="class_level"
    )
    stream = models.ForeignKey(
        Stream, on_delete=models.CASCADE, blank=True, related_name="class_stream"
    )
    class_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True)
    grade_level = models.ForeignKey(
        GradeLevel, blank=True, null=True, on_delete=models.SET_NULL
    )
    capacity = models.PositiveIntegerField(default=40, blank=True)
    occupied_sits = models.PositiveIntegerField(default=0, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "stream"], name="unique_classroom")
        ]

    def __str__(self):
        return f"{self.name} {self.stream}" if self.stream else str(self.name)

    @property
    def available_sits(self):
        return self.capacity - self.occupied_sits

    @property
    def class_status(self):
        percentage = (self.occupied_sits / self.capacity) * 100
        return f"{percentage:.2f}%"

    def clean(self):
        if self.occupied_sits > self.capacity:
            raise ValidationError("Occupied sits cannot exceed the capacity.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Topic(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    class_room = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, blank=True, null=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.name


class SubTopic(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class AllocatedSubject(models.Model):
    teacher_name = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="allocated_subjects"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.OneToOneField(Term, on_delete=models.SET_NULL, blank=True, null=True)
    class_room = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="subjects"
    )
    weekly_periods = models.IntegerField(help_text="Total number of periods per week.")
    max_daily_periods = models.IntegerField(
        default=2,
        help_text="Maximum number of periods allowed per day for this subject.",
    )

    def __str__(self):
        return f"{self.teacher_name} - {self.subject} ({self.academic_year})"

    def subjects_data(self):
        return list(self.subject.all())


class Parent(models.Model):
    first_name = models.CharField(
        max_length=300, verbose_name="First Name", blank=True, null=True
    )
    middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Middle Name"
    )
    last_name = models.CharField(
        max_length=300, verbose_name="Last Name", blank=True, null=True
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICE, blank=True, null=True
    )
    email = models.EmailField(blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    parent_type = models.CharField(
        choices=PARENT_CHOICE, max_length=10, blank=True, null=True
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(
        max_length=150, unique=True, help_text="Personal phone number"
    )
    national_id = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(
        max_length=255, blank=True, null=True, help_text="Current occupation"
    )
    monthly_income = models.FloatField(
        help_text="Parent's average monthly income", blank=True, null=True
    )
    single_parent = models.BooleanField(
        default=False, blank=True, help_text="Is he/she a single parent"
    )
    alt_email = models.EmailField(blank=True, null=True, help_text="Personal email")
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="Parent_images", blank=True)
    inactive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Create a user account for the parent if not exists
        user, created = CustomUser.objects.get_or_create(
            email=self.email,
            defaults={
                "first_name": self.first_name,
                "last_name": self.last_name,
                "is_parent": True,
            },
        )
        if created:
            user.set_password(f"{self.first_name}{self.last_name}".lower())
            user.save()

        # Assign to "parent" group
        group, _ = Group.objects.get_or_create(name="parent")
        user.groups.add(group)


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150, null=True, verbose_name="First Name")
    middle_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Middle Name"
    )
    last_name = models.CharField(max_length=150, null=True, verbose_name="Last Name")
    graduation_date = models.DateField(blank=True, null=True)
    grade_level = models.ForeignKey(
        GradeLevel, blank=True, null=True, on_delete=models.SET_NULL
    )
    class_of_year = models.ForeignKey(
        ClassYear, blank=True, null=True, on_delete=models.SET_NULL
    )
    date_dismissed = models.DateField(blank=True, null=True)
    reason_left = models.ForeignKey(
        ReasonLeft, blank=True, null=True, on_delete=models.SET_NULL
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICE, blank=True, null=True
    )
    religion = models.CharField(
        max_length=50, choices=RELIGION_CHOICE, blank=True, null=True
    )
    region = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    parent_guardian = models.ForeignKey(
        Parent, on_delete=models.CASCADE, blank=True, null=True, related_name="children"
    )
    parent_contact = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True)
    admission_date = models.DateTimeField(auto_now_add=True)
    admission_number = models.CharField(max_length=50, blank=True, unique=True)
    prem_number = models.CharField(max_length=50, blank=True)
    siblings = models.ManyToManyField("self", blank=True)
    image = models.ImageField(upload_to="Student_images", blank=True)
    cache_gpa = models.DecimalField(
        editable=False, max_digits=5, decimal_places=2, blank=True, null=True
    )
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Debt: {self.debt}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()

    def clean(self):
        # Prevent students from being teachers
        if Teacher.objects.filter(id=self.id).exists():
            raise ValidationError("A person cannot be both a student and a teacher.")
        super().clean()

    def save(self, *args, **kwargs):
        # Create parent if not exists
        if self.parent_contact:
            parent, _ = Parent.objects.get_or_create(
                phone_number=self.parent_contact,
                defaults={
                    "first_name": self.middle_name,
                    "last_name": self.last_name,
                    "email": f"parent_{self.first_name}_{self.last_name}@example.com",
                },
            )
            self.parent_guardian = parent
        super().save(*args, **kwargs)

    def update_debt(self, term_fee):
        """
        Add term fee to the student's debt.
        """
        self.debt += Decimal(term_fee)
        self.save()

    def clear_debt(self, amount_paid):
        """
        Reduce the student's debt by the amount paid.
        """
        self.debt -= Decimal(amount_paid)
        self.debt = max(self.debt, Decimal("0.00"))  # Prevent negative debt
        self.save()

    def update_debt_for_term(self, term):
        """
        Update student debt at the start of a new term.
        If moving to a new academic year, carry forward unpaid debt.
        """
        if term.start_date <= timezone.now():
            self.debt += term.default_term_fee  # Add the term fee to existing debt
            self.save()

    def carry_forward_debt_to_new_academic_year(self):
        """
        Carry forward debt to the first term of the new academic year.
        """

        current_academic_year = AcademicYear.objects.get(current=True)
        next_year = AcademicYear.objects.filter(
            start_date__gt=current_academic_year.end_date
        ).first()

        if next_year:
            first_term_of_new_year = (
                Term.objects.filter(academic_year=next_year)
                .order_by("start_date")
                .first()
            )
            if first_term_of_new_year:
                self.update_debt_for_term(first_term_of_new_year)


class StudentClass(models.Model):
    """
    This is a bridge table to link a student to a class.
    When you add a student to a class, we update the selected class capacity.
    """

    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="class_student"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    student_id = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_class"
    )

    @property
    def is_current_class(self):
        # Check if the class belongs to the current academic session
        return self.academic_year.is_current_session

    def __str__(self):
        return str(self.student_id)

    def update_class_table(self):
        selected_class = ClassRoom.objects.get(pk=self.classroom.pk)
        # Using F() expression for atomic update of occupied_sits
        selected_class.occupied_sits = F("occupied_sits") + 1
        selected_class.save()

    def save(self, *args, **kwargs):
        # Update class sits before saving the StudentClass
        self.update_class_table()
        super().save(*args, **kwargs)


class StudentsMedicalHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    history = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="students_medical_files", blank=True, null=True)

    def __str__(self):
        return f"Medical History for {self.student}"

    def clean(self):
        # You can add validation if a file is uploaded and ensure it meets the constraints
        if not self.history and not self.file:
            raise ValidationError(
                "At least one of 'history' or 'file' must be provided."
            )


class StudentsPreviousAcademicHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    former_school = models.CharField(max_length=255, help_text="Former school name")
    last_gpa = models.FloatField()
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Indicate student's academic performance according to your observation",
    )
    academic_record = models.FileField(
        upload_to="students_former_academic_files", blank=True
    )

    def __str__(self):
        return f"Previous Academic History for {self.student}"

    def clean(self):
        # You can add validation for the file field if needed
        if not self.former_school:
            raise ValidationError("Former school name is required.")


class Dormitory(models.Model):
    name = models.CharField(max_length=150)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    occupied_beds = models.IntegerField(blank=True, null=True)
    captain = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name

    def available_beds(self):
        total = self.capacity - self.occupied_beds
        if total <= 0:
            return 0  # Return 0 to indicate no available beds
        return total

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if (
            self.capacity is not None
            and self.occupied_beds is not None
            and self.capacity <= self.occupied_beds
        ):
            raise ValueError(
                f"All beds in {self.name} are occupied. Please add more beds or allocate to another dormitory."
            )
        super(Dormitory, self).save()


class DormitoryAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE)
    date_from = models.DateField(auto_now_add=True)
    date_till = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.student.admission_number)

    @transaction.atomic
    def update_dormitory(self):
        """Update the capacity of the selected dormitory."""
        selected_dorm = Dormitory.objects.select_for_update().get(pk=self.dormitory.pk)
        if selected_dorm.available_beds() <= 0:
            raise ValidationError(f"{selected_dorm.name} has no available beds.")
        selected_dorm.occupied_beds += 1
        selected_dorm.save()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.update_dormitory()
        super(DormitoryAllocation, self).save()


class StudentFile(models.Model):
    file = models.FileField(
        upload_to="students_files/%(student_id)s/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "png", "docx"])
        ],
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.student)

    def clean(self):
        """Override to validate file size or type if necessary."""
        if self.file.size > 10 * 1024 * 1024:  # Limit to 10MB files
            raise ValidationError("File size must be under 10MB.")
        super().clean()


class StudentHealthRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    record = models.TextField()

    def __str__(self):
        return str(self.student)

    def clean(self):
        """Ensure that the record contains appropriate information."""
        if len(self.record) < 10:  # Ensure some minimal content in the record
            raise ValidationError("Health record must contain more information.")
        super().clean()


class MessageToParent(models.Model):
    """Store a message to be shown to parents for a specific amount of time."""

    message = models.TextField(help_text="Message to be shown to Parents.")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.message

    def clean(self):
        """Ensure that end date is not before start date."""
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before the start date.")
        super().clean()

    @property
    def is_active(self):
        """Check if the message is currently active."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class MessageToTeacher(models.Model):
    """Stores a message to be shown to Teachers for a specific amount of time."""

    message = models.TextField(help_text="Message to be shown to Teachers.")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.message

    def clean(self):
        """Ensure that end date is not before start date."""
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before the start date.")
        super().clean()

    @property
    def is_active(self):
        """Check if the message is currently active."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class FamilyAccessUser(CustomUser):
    """A person who can log into the non-admin side and see the same view as a student."""

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """Override save to assign user to 'family' group."""
        super(FamilyAccessUser, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name="family")
        if not self.groups.filter(name="family").exists():
            self.groups.add(group)
