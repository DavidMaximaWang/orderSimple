from django.shortcuts import render

from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import transaction

from .models import Order
from . import models
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer
from .serializers import OrderSerializer
from .renderers import OrderJSONRenderer


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,   mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    lookup_field = 'pk'
    queryset = Order.objects.all()
    renderer_classes = (OrderJSONRenderer,)
    serializer_class = OrderSerializer

    def create(self, request):
        try:
            with transaction.atomic():
                inventory_id = request.data.get("inventory_id")
                inventory = Inventory.objects.get(pk=inventory_id)

                serializer_data = request.data
                if request.data.get("status", True):
                    inventory.quantity = inventory.quantity - \
                        request.data.get("quantity",1)
                    inventory.save()

                #put inventory pk to serialized data
                serializer_data["inventory"] = inventory.pk

                serializer = self.serializer_class(data=serializer_data)

                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({**serializer.data,
                                 "inventory_id": inventory.pk,
                                 "inventory": InventorySerializer(inventory).data},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            if inventory and inventory.quantity < 0:
                raise serializers.ValidationError(
                    'Not enough quantity, product quantity is less than  ' + str(request.data.get("quantity")))
            else:
                raise serializers.ValidationError(
                    'Unknown error, the Order is not created')

    def update(self, request, pk):
        try:
            with transaction.atomic():
                serializer_instance = self.queryset.get(pk=pk)
                prev_quantity = serializer_instance.quantity
                prev_status = serializer_instance.status
                curr_status = request.data.get("status", True)
                curr_quantity = request.data.get("quantity")

                inventory = serializer_instance.inventory

                if prev_status == curr_status and prev_quantity == curr_quantity:
                    pass
                else:
                    quantity_diff = prev_quantity * prev_status - curr_quantity * curr_status

                    if quantity_diff != 0:  # product quantity changed, update the inventory
                        inventory.quantity = inventory.quantity + quantity_diff
                        inventory.save()

                serializer = self.serializer_class(
                    serializer_instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            if inventory and inventory.quantity <= 0:
                raise serializers.ValidationError(
                    'Not enough quantity, product quantity is less than  ' + str(request.data.get("quantity")))
            else:
                raise serializers.ValidationError(
                    'Unknown error, the Order is not updated')

    def destroy(self, request, pk):
        try:
            with transaction.atomic():
                serializer_instance = self.queryset.get(pk=pk)

                inventory = serializer_instance.inventory
                order_quantity = serializer_instance.quantity
                inventory.quantity = inventory.quantity + order_quantity
                inventory.save()
                serializer_instance.delete()
                import time
                time.sleep(1)  # prevent [Errno 104] Connection reset by peer
                return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise NotFound('Order is not deleted')
