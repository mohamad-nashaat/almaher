# Generated by Django 3.1.7 on 2021-05-26 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('level', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('person_id', models.IntegerField(primary_key=True, serialize=False)),
                ('type_id', models.CharField(choices=[('Teacher', 'Teacher'), ('Student', 'Student'), ('Graduate', 'Graduate')], max_length=50, null=True)),
                ('first_name', models.CharField(max_length=120, null=True)),
                ('last_name', models.CharField(max_length=120, null=True)),
                ('father_name', models.CharField(max_length=120, null=True)),
                ('home_number', models.CharField(max_length=120, null=True)),
                ('phone_number', models.CharField(max_length=120, null=True)),
                ('job', models.CharField(max_length=120, null=True)),
                ('address', models.CharField(max_length=120, null=True)),
                ('bdate', models.DateField(null=True)),
                ('priority_id', models.CharField(choices=[('مستمر', 'مستمر'), ('غير معروف', 'غير معروف')], max_length=50, null=True)),
                ('status', models.BooleanField(default=True, null=True)),
                ('create_date', models.DateField(auto_now_add=True, null=True)),
                ('level_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='level.level')),
            ],
        ),
    ]
