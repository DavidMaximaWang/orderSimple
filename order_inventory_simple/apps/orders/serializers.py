from rest_framework import serializers
from django.db.models import F

from .models import Order, OrderedItem
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer

class OrderedItemCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderedItem
        fields = ('id', 'quantity', 'product')

    def save(self, *args, **kwargs):
            super().save(*args, **kwargs)

    def create(self, validated_data):

        instance = OrderedItem.objects.create(**validated_data)

        return instance

   
class OrderedItemDetailedSerializer(serializers.ModelSerializer):
    product = InventorySerializer()

    class Meta:
        model = OrderedItem
        fields = ( 'id', 'quantity', 'product')


class OrderSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255, required=True)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')
    status  = serializers.BooleanField(required=False, allow_null=True)
    ordered_items = OrderedItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'email', 'status',
                  'createdAt', 'updatedAt','ordered_items', 'total_price')

    def validate(self, data):
        
        ordered_items = data.get('ordered_items', None)
        if ordered_items is None:
            raise serializers.ValidationError("Must order some items")
        if ordered_items:
            for ordered_item in ordered_items:
                if ordered_item.get('product').quantity< ordered_item.get('quantity'):
                    raise serializers.ValidationError("Out of stock, no enough this product")
        return data

    def create(self, validated_data):
        request = self.context.get('request', None)

        order_items = validated_data.pop('ordered_items')
        instance = Order.objects.create( **validated_data)
        for order_item in order_items:
            instance.ordered_items.create(**order_item)

        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        ordered_items = validated_data.pop('ordered_items', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value) 
              
        instance.save()

        if ordered_items is not None:
            prev_all_items = instance.ordered_items.all().delete()

            for ordered_item in ordered_items:
                created_ordered_item = instance.ordered_items.create(
                    **ordered_item)

        return instance


    def get_created_at(self, instance):

        return instance.created_at.isoformat()

    def get_updated_at(self, instance):

        return instance.updated_at.isoformat()


class OrderDetailedSerializer(serializers.ModelSerializer):
    ordered_items = OrderedItemDetailedSerializer(many=True)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Order
        fields = ('id', 'email', 'status',
                  'createdAt', 'updatedAt','ordered_items', 'total_price')

    def get_created_at(self, instance):
    
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):

        return instance.updated_at.isoformat()

