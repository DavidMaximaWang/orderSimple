from rest_framework import serializers

from .models import Order
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer


class OrderSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255, required=True)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')
    status  = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ('email', 'status',
                  'createdAt', 'updatedAt','quantity', 'inventory')
    


    def create(self, validated_data):
                         
        return Order.objects.create( **validated_data)

    def get_created_at(self, instance):

        return instance.created_at.isoformat()

    def get_updated_at(self, instance):

        return instance.updated_at.isoformat()
