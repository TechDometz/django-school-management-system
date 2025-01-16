# Generated by Django 5.1 on 2025-01-16 12:40

import datetime
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0010_rename_students_name_studentspreviousacademichistory_student_and_more'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancestatus',
            name='absent',
            field=models.BooleanField(default=False, help_text='Used for different types of absent statuses.'),
        ),
        migrations.AlterField(
            model_name='attendancestatus',
            name='code',
            field=models.CharField(help_text="Short code used on attendance reports. Example: 'A' might be the code for 'Absent'.", max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='attendancestatus',
            name='half',
            field=models.BooleanField(default=False, help_text='Indicates half-day attendance. Do not check absent, otherwise it will double count.'),
        ),
        migrations.AlterField(
            model_name='attendancestatus',
            name='late',
            field=models.BooleanField(default=False, help_text='Used for tracking late statuses.'),
        ),
        migrations.AlterField(
            model_name='attendancestatus',
            name='name',
            field=models.CharField(help_text='"Present" will not be saved but may show as an option for teachers.', max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='PeriodAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('period', models.IntegerField()),
                ('reason_for_absence', models.CharField(blank=True, max_length=500, null=True)),
                ('notes', models.CharField(blank=True, max_length=500)),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.attendancestatus')),
                ('student', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='academic.student')),
            ],
            options={
                'ordering': ('date', 'student', 'period'),
                'unique_together': {('student', 'date', 'period')},
            },
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('notes', models.CharField(blank=True, max_length=500)),
                ('ClassRoom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.classroom')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.attendancestatus')),
                ('student', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='academic.student')),
            ],
            options={
                'ordering': ('-date', 'student'),
                'unique_together': {('student', 'date', 'status')},
            },
        ),
    ]
