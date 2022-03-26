# Generated by Django 3.1.7 on 2022-03-26 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0001_initial'),
        ('session', '0001_initial'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='person_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='persons_attendance', to='person.person'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='session_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessions_attendance', to='session.session'),
        ),
    ]