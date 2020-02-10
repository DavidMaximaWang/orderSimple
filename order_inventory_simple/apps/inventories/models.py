from django.db import models
from ..core.models import TimeStampModel


class Inventory(TimeStampModel):
    status = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True,
                            default='', db_index=True)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1, blank=False)
    
    @property
    def ordered_quantity(self):
        return sum([item.quantity for item in self.ordered_items.all()])

    def __str__(self):
        return self.name

    
    # def to_representation(self, value):
    #     return value
