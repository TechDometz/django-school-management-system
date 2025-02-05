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
        blank=True, null=True, help_text="Rank for subject reports"
    )

    class Meta:
        ordering = ("order_rank", "name")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()

        super().save(*args, **kwargs)


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

    class Meta:
        ordering = ["subject_code"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def save(self, *args, **kwargs):
        # Generate description
        self.name = self.name.lower()
        self.description = f"{self.name.lower()} - {self.subject_code}"

        super().save(*args, **kwargs)


class Teacher(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="teacher",
        null=True,
        blank=True,
    )
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
        ordering = ("id","first_name", "last_name")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def deleted(self):
        return self.inactive

    def save(self, *args, **kwargs):
        """
        When an teacher is created, generate a CustomUser instance for login.
        """
        # Generate unique username
        if not self.username:
            self.username = f"{self.first_name.lower()}{self.last_name.lower()}{get_random_string(4)}"

        if not self.user:
            # Create the user if it doesn't exist
            user = CustomUser.objects.create(
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                is_teacher=True,
            )

            # Set a default password using empId (if available) or fallback
            default_password = f"Complex.{self.empId[-4:] if self.empId and len(self.empId) >= 4 else '0000'}"
            user.set_password(default_password)
            user.save()

            # Attach the created user to the teacher
            self.user = user

            # Add user to "teacher" group
            group, _ = Group.objects.get_or_create(name="teacher")
            user.groups.add(group)

        super().save(*args, **kwargs)

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


class GradeLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Grade Level")
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class ClassLevel(models.Model):
    id = models.IntegerField(unique=True, primary_key=True, verbose_name="Class Level")
    name = models.CharField(max_length=150, unique=True)
    grade_level = models.ForeignKey(
        GradeLevel, blank=True, null=True, on_delete=models.SET_NULL
    )

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

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)


class ClassRoom(models.Model):
    name = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, blank=True, related_name="class_level"
    )
    stream = models.ForeignKey(
        Stream, on_delete=models.CASCADE, blank=True, related_name="class_stream"
    )
    class_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True)
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
    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, blank=True, null=True
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
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="parent",
        null=True,
        blank=True,
    )
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

    class Meta:
        ordering = ["email", "first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def save(self, *args, **kwargs):
        """
        When an parent is created, generate a CustomUser instance for login.
        """

        if not self.user:
            # Create the user if it doesn't exist
            user = CustomUser.objects.create(
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                is_parent=True,
            )

            # Set a default password using empId (if available) or fallback
            default_password = f"Complex.0000"
            user.set_password(default_password)
            user.save()

            # Attach the created user to the parent
            self.user = user

            # Add user to "parent" group
            group, _ = Group.objects.get_or_create(name="parent")
            user.groups.add(group)

        super().save(*args, **kwargs)

        # Optionally send email (integrate email backend here)


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150, null=True, verbose_name="First Name")
    middle_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Middle Name"
    )
    last_name = models.CharField(max_length=150, null=True, verbose_name="Last Name")
    graduation_date = models.DateField(blank=True, null=True)
    class_level = models.ForeignKey(
        ClassLevel, blank=True, null=True, on_delete=models.SET_NULL
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

    class Meta:
        ordering = ["admission_number","last_name", "first_name"]

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name} - Debt: {self.debt}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()

    def clean(self):
        # Prevent students from being teachers
        if Teacher.objects.filter(id=self.id).exists():
            raise ValidationError("A person cannot be both a student and a teacher.")
        super().clean()

    def save(self, *args, **kwargs):
        # Validate parent_contact presence
        if not self.parent_contact:
            raise ValidationError("Parent contact is required.")

        # Create parent if not exists
        parent, created = Parent.objects.get_or_create(
            phone_number=self.parent_contact,
            defaults={
                "first_name": self.middle_name or "Unknown",
                "last_name": self.last_name,
                "email": f"parent_of_{self.first_name}_{self.last_name}@hayatul.com",
                "phone_number": self.parent_contact,
            },
        )

        self.parent_guardian = parent

        # Check for existing siblings
        existing_sibling = (
            Student.objects.filter(parent_contact=self.parent_contact)
            .exclude(id=self.id)
            .first()
        )
        self.first_name = self.first_name.lower()
        self.middle_name = self.middle_name.lower()
        self.last_name = self.last_name.lower()
        super().save(*args, **kwargs)

        if existing_sibling:
            # Link siblings
            self.siblings.add(existing_sibling)
            existing_sibling.siblings.add(self)

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
    Bridge table to link a student to a class.
    Updates the selected class capacity when a student is added or removed.
    """

    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="class_students"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_classes",
        blank=True,
        null=True,
    )

    @property
    def is_current_class(self):
        return self.academic_year.is_current_session

    def __str__(self):
        return f"Student: {self.student}, Class: {self.classroom}"

    def clean(self):
        """
        Perform custom validations:
        - Ensure the classroom matches the student's class level.
        - Check if the classroom has available seats.
        - Prevent duplicate assignments for the same student and academic year.
        """
        # Validate that the classroom matches the student's class level
        if self.classroom.name != self.student.class_level:
            raise ValidationError(
                f"The classroom '{self.classroom.name}' does not match the student's class level '{self.student.class_level}'."
            )

        # Validate that the classroom has available seats
        if not self.pk and self.classroom.occupied_sits >= self.classroom.capacity:
            raise ValidationError(
                f"The classroom '{self.classroom}' has reached its maximum capacity."
            )

        # Check for duplicate StudentClass assignments
        if (
            StudentClass.objects.filter(
                classroom=self.classroom,
                academic_year=self.academic_year,
                student=self.student,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                f"The student '{self.student}' is already assigned to this class for the academic year '{self.academic_year}'."
            )

    def update_class_table(self, increment=True):
        """
        Updates the `occupied_sits` count in the classroom manually within a transaction.
        """
        # Use a transaction to ensure consistency
        with transaction.atomic():
            selected_class = ClassRoom.objects.select_for_update().get(
                pk=self.classroom.pk
            )

            if increment:
                # Check capacity before incrementing
                if selected_class.occupied_sits >= selected_class.capacity:
                    raise ValidationError(
                        "This class has reached its maximum capacity."
                    )
                selected_class.occupied_sits += 1
            else:
                # Ensure occupied_sits doesn't go below zero
                if selected_class.occupied_sits <= 0:
                    raise ValidationError("Cannot have negative occupied sits.")
                selected_class.occupied_sits -= 1

            # Save the updated classroom instance
            selected_class.save()

    def save(self, *args, **kwargs):
        """
        Override the save method to:
        - Validate before saving.
        - Update the classroom's capacity on creation.
        """
        if not self.pk:  # Only increment capacity on creation
            self.update_class_table(increment=True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override the delete method to:
        - Decrement the classroom's capacity when a record is deleted.
        """
        self.update_class_table(increment=False)
        super().delete(*args, **kwargs)

    def delete_queryset(self, request, queryset):
        """
        Override the bulk delete behavior to update `occupied_sits` correctly.
        """
        with transaction.atomic():  # Ensure the operation is transactional
            for instance in queryset:
                instance.update_class_table(increment=False)  # Decrement capacity
            queryset.delete()  # Perform the actual deletion


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
