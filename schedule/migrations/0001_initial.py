# Generated by Django 5.1 on 2025-01-16 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academic', '0003_allocatedsubject_delete_subjectallocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.classroom')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.allocatedsubject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.teacher')),
            ],
            options={
                'unique_together': {('day_of_week', 'start_time', 'classroom')},
            },
        ),
    ]
