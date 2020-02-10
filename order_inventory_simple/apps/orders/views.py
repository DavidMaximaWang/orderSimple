from django.shortcuts import render

from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView
from django.db import transaction

from .models import Order, OrderedItem
from . import models
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer
from .serializers import OrderSerializer, OrderDetailedSerializer, OrderedItemCreateSerializer
from .renderers import OrderJSONRenderer


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,   mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    lookup_field = 'pk'
    queryset = Order.objects.all()
    renderer_classes = (OrderJSONRenderer,)
    serializer_class = OrderSerializer
    read_serializer_class = OrderDetailedSerializer

    def create(self, request):
        try:
            serializer_context = {'request': request, "create": True}
            write_serializer = self.serializer_class(data=request.data, context=serializer_context)

            write_serializer.is_valid(raise_exception=True)
            write_serializer.save()
            read_serializer = self.read_serializer_class(write_serializer.instance, context=serializer_context)
        except Exception as e:
            a= type(e)
            raise e
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, pk):
        try:
            serializer_instance = self.queryset.get(pk=pk)
        except Order.DoesNotExist:
            raise NotFound("Not found an order with this order id")   

        serializer_context = {'request': request, "update": True}
        
        
        serializer = self.serializer_class(
            serializer_instance, data=request.data, context=serializer_context, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, pk):
        try:
            serializer_instance = self.queryset.get(pk=pk)
        except Order.DoesNotExist:
            raise NotFound("Not found an order with this order id")
        serializer_instance.ordered_items.all().delete() #trigger the pre_delete to update the inventory
        serializer_instance.delete()
  
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class OrderItemAPIView(APIView):
    serializer_class = OrderSerializer

    def delete(self, request,  order_id=None):
        serializer_context = {'request': request}

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound("Not found an order with this order id")
        except OrderedItem.DoesNotExist:
            raise NotFound("Not found an order item with this ordered item id")

        order.remove_order_item(request.data.get('item_id', None))

        serializer = self.serializer_class(order, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, order_id=None):
        serializer_context = {'request': request}

        try:
            order = Order.objects.get(id=order_id)
            product = Inventory.objects.get(id=request.data.get('product', None))
            request.data['product' ]= product
        except Order.DoesNotExist:
            raise NotFound("Not found an order with this order id")
        except Inventory.DoesNotExist:
            raise NotFound("Not found a product with this product id")
           
        order.add_order_item(request.data)
        serializer = self.serializer_class(order, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
