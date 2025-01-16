# Generated by Django 5.1 on 2025-01-16 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_no', models.IntegerField(unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('paid_to', models.CharField(max_length=255, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('abbr', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_no', models.IntegerField(unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('payer', models.CharField(max_length=255, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('abbr', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
