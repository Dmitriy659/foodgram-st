from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=128, null=False)
    measurement_unit = models.CharField(max_length=64, null=False)

    def __str__(self):
        return self.name
