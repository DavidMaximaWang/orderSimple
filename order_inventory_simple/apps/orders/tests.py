import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer

from .models import Order
from .serializers import OrderSerializer


def setUpInventory(__self):
    __self.first = Inventory.objects.create(
        name='test_product101', description="good101", price=321.22, quantity=300)
    __self.second = Inventory.objects.create(
        name='test_product102', description="good102", price=322.22)
    __self.third = Inventory.objects.create(
        name='test_product103', description="good103", price=323.22)
    __self.fourth = Inventory.objects.create(
        name='test_product104', description="good104", price=324.22)

class GetAllOrders(APITestCase):

    def setUp(self):
        setUpInventory(self)
        order_data = {"email": "test@test.com", "inventory_id": self.first.pk,
                 "quantity": 10}
        #create 3 orders
        for i in range(3):
            self.client.post(reverse("orders:order-list"), data=json.dumps(order_data),
                                    content_type='application/json')

    def test_get_all_orders(self):
        inventory =Inventory.objects.get(pk=self.first.pk)
        updated_quantity = InventorySerializer(inventory).data.get("quantity", None)
        self.assertEqual(updated_quantity, 270)
        #test the quantity in corresponding inventory has been changed

        expected = Order.objects.all()
        response = self.client.get(reverse("orders:order-list"))

        serializer = OrderSerializer(expected, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewOrderTest(APITestCase):
    
    def setUp(self):
        setUpInventory(self)
        self.valid_payload= {"email": "test1@test.com", "inventory_id": self.first.pk}
        self.invalid_payload= {"email": "test1@test.com", "inventory_id": self.first.pk, "quantity":301}
        

    def test_create_valid_single_order(self):
        response = self.client.post(reverse("orders:order-list"), data=json.dumps(self.valid_payload),
                                    content_type='application/json')

        expected = Order.objects.get(email="test1@test.com")

        order_serialized = OrderSerializer(expected)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized= InventorySerializer(inventory)

        self.assertEqual(response.data, {**order_serialized.data,
                                 "inventory_id": self.first.pk,
                                 "inventory": inventory_serialized.data})

    def test_create_invalid_single_order(self):
        response = self.client.post(reverse("orders:order-list"), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized= InventorySerializer(inventory)

        self.assertEqual(inventory_serialized.data.get("quantity"), 300)


class UpdateSingleOrderTest(APITestCase):
    """ Test module for updating an existing inventory record """

    def setUp(self):
        setUpInventory(self)
        order_data = {"email": "test@test.com", "inventory_id": self.first.pk,
                 "quantity": 10}

        #create an order for product 'test_product101'
        self.test_order_res=self.client.post(reverse("orders:order-list"), data=json.dumps(order_data),
                                    content_type='application/json')
        self.invalid_payload = {
            'quantity': 301,
        }
        self.valid_payload = {
            'quantity': 100,
        }
        self.valid_payload1 = {
            "email": "test@test.com",
            "inventory_id": self.first.pk,
            'status': 0,
            'quantity':10
        }

    def test_valid_update_inventory(self):
        self.assertEqual(self.test_order_res.data.get("inventory").get("quantity"),290)

        order = Order.objects.get(email="test@test.com")
        order_serialized = OrderSerializer(order)

        #update quantity
        response = self.client.put(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"),200)


        #update status
        response = self.client.put(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}),
            data=json.dumps(self.valid_payload1),
            content_type='application/json'
        )

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 300)

    def test_invalid_update_inventory(self):
        self.assertEqual(self.test_order_res.data.get("inventory").get("quantity"),290)

        order = Order.objects.get(email="test@test.com")
        order_serialized = OrderSerializer(order)

        #update quantity
        response = self.client.put(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        s = "Not enough quantity, product quantity is less than  301"
        self.assertIn(s, str(response.data))
  
        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 290)# inventory unchanged

class DeleteSingleOrderTest(APITestCase):
    """ Test module for deleting an existing inventory record """

    def setUp(self):
        setUpInventory(self)
        order_data1 = {"email": "test1@test.com", "inventory_id": self.first.pk,
                 "quantity": 10}
        order_data2 = {"email": "test2@test.com", "inventory_id": self.first.pk,
                 "quantity": 10}         
        
        #create 2 orders
        self.client.post(reverse("orders:order-list"), data=json.dumps(order_data1),
                                    content_type='application/json')
        self.client.post(reverse("orders:order-list"), data=json.dumps(order_data2),
                                    content_type='application/json')

    def test_valid_delete_order(self):

        order = Order.objects.get(email="test1@test.com")
        order_serialized = OrderSerializer(order)

        response = self.client.delete(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 290)
        #before delete order, the product quantity was 280

    def test_invalid_delete_order(self):
        response = self.client.delete(
            reverse("orders:order-detail", kwargs={'pk': 1000}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
