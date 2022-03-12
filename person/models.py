from django.db import models
from level.models import Level

# Create your models here.

class Person(models.Model):
    person_type = (
        ('Teacher','Teacher'),
        ('Student','Student'),
        ('Graduate','Graduate'),
    )
    priority = (
        ('مستمر','مستمر'),
        ('غير معروف','غير معروف'),
    )
    person_id = models.IntegerField(primary_key=True)
    type_id = models.CharField(max_length=50, null=True, choices=person_type)
    first_name = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=120, null=True)
    father_name = models.CharField(max_length=120, null=True)
    home_number = models.CharField(max_length=120, null=True)
    phone_number = models.CharField(max_length=120, null=True)
    job = models.CharField(max_length=120, null=True)
    address = models.CharField(max_length=120, null=True)
    bdate = models.DateField(null=True)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
    priority_id = models.CharField(max_length=50, null=True, choices=priority)
    status = models.BooleanField(default=True, null=True)
    create_date = models.DateField(auto_now_add=True, null=True)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'