from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import OrderViewSet


router = DefaultRouter(trailing_slash=False)

router.register(r'orders', OrderViewSet)

app_name = 'orders'
urlpatterns = [path('', include(router.urls)), ]
