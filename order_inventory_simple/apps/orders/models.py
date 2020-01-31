from django.db import models
from django.core.validators import  MinValueValidator

from ..core.models import TimeStampModel
from ..inventories.models import Inventory


class Order(TimeStampModel):
    email = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    quantity = models.IntegerField(
        default=1, validators=[MinValueValidator(1),])
    inventory = models.ForeignKey(Inventory,
                                  on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.email
