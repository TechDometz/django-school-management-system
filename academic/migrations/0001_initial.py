# Generated by Django 5.1 on 2025-01-16 14:22

import academic.validators
import django.core.validators
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClassLevel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Class Level')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capacity', models.PositiveIntegerField(blank=True, default=40)),
                ('occupied_sits', models.PositiveIntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ClassYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(help_text='Example 2020', max_length=100, unique=True)),
                ('full_name', models.CharField(blank=True, help_text='Example Class of 2020', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('order_rank', models.IntegerField(blank=True, help_text='Rank for course reports', null=True)),
            ],
            options={
                'ordering': ('order_rank', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Dormitory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True)),
                ('occupied_beds', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DormitoryAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_from', models.DateField(auto_now_add=True)),
                ('date_till', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GradeLevel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Grade Level')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='MessageToParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='Message to be shown to Parents.')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='MessageToTeacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='Message to be shown to Teachers.')),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=300, null=True, verbose_name='First Name')),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Middle Name')),
                ('last_name', models.CharField(blank=True, max_length=300, null=True, verbose_name='Last Name')),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('parent_type', models.CharField(blank=True, choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Guardian', 'Guardian')], max_length=10, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(help_text='Personal phone number', max_length=150, unique=True)),
                ('national_id', models.CharField(blank=True, max_length=100, null=True)),
                ('occupation', models.CharField(blank=True, help_text='Current occupation', max_length=255, null=True)),
                ('monthly_income', models.FloatField(blank=True, help_text="Parent's average monthly income", null=True)),
                ('single_parent', models.BooleanField(blank=True, default=False, help_text='Is he/she a single parent')),
                ('alt_email', models.EmailField(blank=True, help_text='Personal email', max_length=254, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(blank=True, upload_to='Parent_images')),
                ('inactive', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReasonLeft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, validators=[academic.validators.stream_validator])),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=150, null=True, verbose_name='First Name')),
                ('middle_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Middle Name')),
                ('last_name', models.CharField(max_length=150, null=True, verbose_name='Last Name')),
                ('graduation_date', models.DateField(blank=True, null=True)),
                ('date_dismissed', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True)),
                ('religion', models.CharField(blank=True, choices=[('Islam', 'Islam'), ('Christian', 'Christian'), ('Other', 'Other')], max_length=50, null=True)),
                ('region', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('street', models.CharField(blank=True, max_length=255)),
                ('blood_group', models.CharField(blank=True, max_length=10, null=True)),
                ('parent_contact', models.CharField(blank=True, max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True)),
                ('admission_date', models.DateTimeField(auto_now_add=True)),
                ('admission_number', models.CharField(blank=True, max_length=50, unique=True)),
                ('prem_number', models.CharField(blank=True, max_length=50)),
                ('image', models.ImageField(blank=True, upload_to='Student_images')),
                ('cache_gpa', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=5, null=True)),
                ('debt', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='StudentClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='StudentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='students_files/%(student_id)s/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png', 'docx'])])),
            ],
        ),
        migrations.CreateModel(
            name='StudentHealthRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='StudentsMedicalHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('history', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='students_medical_files')),
            ],
        ),
        migrations.CreateModel(
            name='StudentsPreviousAcademicHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('former_school', models.CharField(help_text='Former school name', max_length=255)),
                ('last_gpa', models.FloatField()),
                ('notes', models.CharField(blank=True, help_text="Indicate student's academic performance according to your observation", max_length=255)),
                ('academic_record', models.FileField(blank=True, upload_to='students_former_academic_files')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('subject_code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('is_selectable', models.BooleanField(default=False, help_text='Select if subject is optional')),
                ('graded', models.BooleanField(default=True, help_text='Teachers can submit grades')),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SubjectAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='SubTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=250, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=300)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=300)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('empId', models.CharField(blank=True, max_length=8, null=True, unique=True)),
                ('tin_number', models.CharField(blank=True, max_length=9, null=True)),
                ('nssf_number', models.CharField(blank=True, max_length=9, null=True)),
                ('short_name', models.CharField(blank=True, max_length=3, null=True, unique=True)),
                ('isTeacher', models.BooleanField(default=True)),
                ('salary', models.IntegerField(blank=True, null=True)),
                ('unpaid_salary', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('national_id', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=150)),
                ('alt_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('designation', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Employee_images')),
                ('inactive', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('first_name', 'last_name'),
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
