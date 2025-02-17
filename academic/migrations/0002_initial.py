# Generated by Django 5.1 on 2025-01-16 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academic', '0001_initial'),
        ('administration', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyAccessUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.customuser',),
        ),
        migrations.AddField(
            model_name='classroom',
            name='name',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_level', to='academic.classlevel'),
        ),
        migrations.AddField(
            model_name='dormitoryallocation',
            name='dormitory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.dormitory'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='grade_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academic.gradelevel'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='stream',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_stream', to='academic.stream'),
        ),
        migrations.AddField(
            model_name='student',
            name='class_of_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academic.classyear'),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academic.gradelevel'),
        ),
        migrations.AddField(
            model_name='student',
            name='parent_guardian',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='academic.parent'),
        ),
        migrations.AddField(
            model_name='student',
            name='reason_left',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academic.reasonleft'),
        ),
        migrations.AddField(
            model_name='student',
            name='siblings',
            field=models.ManyToManyField(blank=True, to='academic.student'),
        ),
        migrations.AddField(
            model_name='dormitoryallocation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='dormitory',
            name='captain',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='studentclass',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.academicyear'),
        ),
        migrations.AddField(
            model_name='studentclass',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_student', to='academic.classroom'),
        ),
        migrations.AddField(
            model_name='studentclass',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_class', to='academic.student'),
        ),
        migrations.AddField(
            model_name='studentfile',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='studenthealthrecord',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='studentsmedicalhistory',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='studentspreviousacademichistory',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.student'),
        ),
        migrations.AddField(
            model_name='subject',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.department'),
        ),
        migrations.AddField(
            model_name='subjectallocation',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.academicyear'),
        ),
        migrations.AddField(
            model_name='subjectallocation',
            name='class_room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='academic.classroom'),
        ),
        migrations.AddField(
            model_name='subjectallocation',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocated_subjects', to='academic.subject'),
        ),
        migrations.AddField(
            model_name='subjectallocation',
            name='term',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.term'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='subject_specialization',
            field=models.ManyToManyField(blank=True, to='academic.subject'),
        ),
        migrations.AddField(
            model_name='subjectallocation',
            name='teacher_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.teacher'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='class_teacher',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='academic.teacher'),
        ),
        migrations.AddField(
            model_name='topic',
            name='class_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.classroom'),
        ),
        migrations.AddField(
            model_name='topic',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.subject'),
        ),
        migrations.AddField(
            model_name='subtopic',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='academic.topic'),
        ),
        migrations.AddConstraint(
            model_name='classroom',
            constraint=models.UniqueConstraint(fields=('name', 'stream'), name='unique_classroom'),
        ),
    ]
