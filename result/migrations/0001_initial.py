# Generated by Django 3.1.7 on 2021-05-26 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('session', '0001_initial'),
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('result_id', models.IntegerField(primary_key=True, serialize=False)),
                ('attendance', models.IntegerField(null=True)),
                ('theoretical_mark', models.IntegerField(null=True)),
                ('practical_mark', models.IntegerField(null=True)),
                ('result', models.IntegerField(null=True)),
                ('result_type', models.CharField(choices=[('ناجح', 'ناجح'), ('نجاح شرطي', 'نجاح شرطي'), ('إعادة', 'إعادة')], max_length=50, null=True)),
                ('create_date', models.DateField(auto_now_add=True, null=True)),
                ('session_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='session.session')),
                ('student_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='person.person')),
            ],
        ),
    ]
