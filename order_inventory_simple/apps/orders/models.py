from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete, post_save, pre_save
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from ..core.models import TimeStampModel
from ..inventories.models import Inventory


class Order(TimeStampModel):
    email = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    
    @property
    def total_price(self):
        return sum([item.product.price * item.quantity for item in self.ordered_items.select_related('product').all()])

    def __str__(self):
        return self.email


    def add_order_item(self, order_item_dict):
        # do not allow same product in order items twice  
        if self.ordered_items.filter(product=order_item_dict.get('product', None)).exists():
            raise ValidationError("item exists already")
        self.ordered_items.create(**order_item_dict)

    def remove_order_item(self, order_item_id):
        self.ordered_items.filter(id=order_item_id).delete()
        
    
    def has_order_item(self, order_item):
        return self.ordered_items.filter(pk=order_item.pk).exists()


class OrderedItem(models.Model):
    order = models.ForeignKey(
        'Order', related_name='ordered_items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        'inventories.Inventory', related_name='ordered_items', on_delete=models.PROTECT) #do not delete product when all orders deleted
    quantity = models.IntegerField(default=1)#order number 0 for an item makes no sense


@receiver(post_save, sender=OrderedItem)
def save_change_inventory(sender, instance, created, *args, **kwargs):
    quantity = instance.quantity
    product_id = instance.product.id
    product = Inventory.objects.get(id=product_id)#get product from the db, it could have been changed 
    if  not product.status:
        raise ValidationError("Can not order this product(name:{0}), the product status is not active".format(product.name)) 
       
    product.quantity = product.quantity - quantity

    if product.quantity<0:
        raise ValidationError("Out of stock, no enough this product: {0}".format(product.name)) 

    product.save()

@receiver(pre_delete, sender=OrderedItem)
def pre_delete_change_inventory(sender, instance, *args, **kwargs):
    quantity = instance.quantity
    product_id = instance.product.id
    product = Inventory.objects.get(id=product_id)

    product.quantity = product.quantity + quantity
    product.save() 


        
