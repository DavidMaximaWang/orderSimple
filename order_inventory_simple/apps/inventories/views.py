from django.shortcuts import render

from rest_framework import serializers, status, generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


from .models import Inventory
from .serializers import InventorySerializer
from .renderers import InventoryJSONRenderer


class InventoryViewSet(mixins.CreateModelMixin,mixins.ListModelMixin,   mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = Inventory.objects.all()
    renderer_classes = (InventoryJSONRenderer,)
    serializer_class = InventorySerializer

    def create(self, request):
        serializer_data = request.data
        name = serializer_data.get("name", None)
        if self.queryset.filter(name=name):
            raise serializers.ValidationError('The inventory exists')

        serializer = self.serializer_class(data=serializer_data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, slug):
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Inventory.DoesNotExist:
            raise NotFound("Inventory with this slug not found")

        serializer = self.serializer_class(
            serializer_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        try:
            inventory = Inventory.objects.get(slug=slug)
        except Inventory.DoesNotExist:
            raise NotFound('Inventory with this slug does not exist')
        
        inventory.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
