from django.db import models


class Level(models.Model):
    level_name = models.CharField(max_length=50, primary_key=True)
    level_id = models.IntegerField(null=True)
    create_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.level_name
