from rest_framework import serializers

from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)

    slug = serializers.SlugField(required=False)
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:

        model = Inventory
        fields = ('name', 'description', 'price',
                  'createdAt', 'updatedAt', 'slug', 'quantity')

    def create(self, validated_data):
        return Inventory.objects.create(**validated_data)

    def get_created_at(self, instance):

        return instance.created_at.isoformat()

    def get_updated_at(self, instance):

        return instance.updated_at.isoformat()
