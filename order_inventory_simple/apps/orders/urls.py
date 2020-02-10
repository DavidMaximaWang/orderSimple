from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, OrderItemAPIView


router = DefaultRouter(trailing_slash=False)

router.register(r'orders', OrderViewSet)

app_name = 'orders'
urlpatterns = [path('', include(router.urls)),
               path('orders/<int:order_id>/order_item',
                    OrderItemAPIView.as_view(), name="order_item"),
               ]
