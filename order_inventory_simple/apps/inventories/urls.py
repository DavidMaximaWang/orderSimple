from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import InventoryViewSet


router = DefaultRouter(trailing_slash=False)

router.register(r'inventories', InventoryViewSet, basename="inventories")

app_name = 'inventories'
urlpatterns = [path('', include(router.urls)),  ]
