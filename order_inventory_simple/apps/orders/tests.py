import simplejson as json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ..inventories.models import Inventory
from ..inventories.serializers import InventorySerializer

from .models import Order
from .serializers import OrderSerializer, OrderDetailedSerializer


def setUpInventory(__self):
    __self.first = Inventory.objects.create(
        name='test_product101', description="good101", price=321.22, quantity=300)
    __self.second = Inventory.objects.create(
        name='test_product102', description="good102", price=322.22, quantity=300)
    __self.third = Inventory.objects.create(
        name='test_product103', description="good103", price=323.22, quantity=300)
    __self.fourth = Inventory.objects.create(
        name='test_product104', description="good104", price=324.22, quantity=300)


class GetAllOrders(APITestCase):

    def setUp(self):
        setUpInventory(self)
        order_data = {"email": "test1@test.com",
                      "ordered_items": [
                          {
                              "quantity": 1,
                              "product": 1
                          },
                          {
                              "quantity": 2,
                              "product": 2
                          },
                          {
                              "quantity": 4,
                              "product": 3
                          }
                      ]}
        #create 3 orders
        for i in range(3):
            self.client.post(reverse("orders:order-list"), data=json.dumps(order_data),
                             content_type='application/json')

    def test_get_all_orders(self):
        product_id_list = [1, 2, 3]
        expect_qt_list = [297, 294, 288]
        inventories = Inventory.objects.filter(
            id__in=product_id_list).order_by('id')
        real_qt_list = [iv.quantity for iv in inventories]

        #test the quantity in corresponding inventory has been changed
        self.assertEqual(real_qt_list == expect_qt_list, True)

        expected = Order.objects.all()
        response = self.client.get(reverse("orders:order-list"))

        serializer = OrderSerializer(expected, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateNewOrderTest(APITestCase):

    def setUp(self):
        setUpInventory(self)
        self.valid_payload = order_data = {"email": "test1@test.com",
                                           "ordered_items": [
                                               {
                                                   "quantity": 1,
                                                   "product": 1
                                               }
                                           ]}
        self.invalid_payload = {"email": "test2@test.com",
                                "ordered_items": [
                                    {
                                        "quantity": 301,
                                        "product": 3
                                    }
                                ]}

    def test_create_valid_single_order(self):
        response = self.client.post(reverse("orders:order-list"), data=json.dumps(self.valid_payload),
                                    content_type='application/json')

        expected = Order.objects.get(email="test1@test.com")

        order_serialized = OrderDetailedSerializer(expected)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)

        #test the created result contain detailed inventory information
        self.assertEqual(response.data, order_serialized.data)
        self.assertIn('test_product101', json.dumps(order_serialized.data))
        self.assertIn('good101', json.dumps(order_serialized.data))

    def test_create_invalid_single_order(self):
        response = self.client.post(reverse("orders:order-list"), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized= InventorySerializer(inventory)

        #inventory for test_product103 not changed
        self.assertEqual(inventory_serialized.data.get("quantity"), 300)


class UpdateSingleOrderTest(APITestCase):
    """ Test module for updating an existing inventory record """

    def setUp(self):
        setUpInventory(self)
        order_data = {"email": "test1@test.com",
                      "ordered_items": [
                          {
                              "quantity": 1,
                              "product": 1
                          }
                      ]}

        #create an order for product 'test_product101'
        self.test_order_res = self.client.post(reverse("orders:order-list"), data=json.dumps(order_data),
                                               content_type='application/json')
        self.invalid_payload = {
            "email": "test@email.com.test",
            "status": True,
            "ordered_items": [
                {
                    "quantity": 2000,
                    "product": 2
                }
            ]
        }
        self.valid_payload = {
            "email": "test@email.com.test",
            "status": True,
            "ordered_items": [
                {
                    "quantity": 2,
                    "product": 2
                }
            ]
        }

    def test_valid_update_inventory(self):
        self.assertEqual(self.test_order_res.data.get(
            "ordered_items")[0].get("quantity"), 1)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 299)  #first product quantity reduced by the order  

        order = Order.objects.get(email="test1@test.com")
        order_serialized = OrderSerializer(order)

        #update order quantity and product
        response = self.client.put(
            reverse("orders:order-detail",
                    kwargs={'pk': order.__dict__.get("id")}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 300)#first product removed from order

        inventory = Inventory.objects.get(pk=self.second.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 298)


#         #update status
#         response = self.client.put(
#             reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}),
#             data=json.dumps(self.valid_payload1),
#             content_type='application/json'
#         )

#         inventory = Inventory.objects.get(pk=self.first.pk)
#         inventory_serialized = InventorySerializer(inventory)
#         self.assertEqual(inventory_serialized.data.get("quantity"), 300)

    def test_invalid_update_inventory(self):
        self.assertEqual(self.test_order_res.data.get(
            "ordered_items")[0].get("quantity"), 1)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 299)    

        order = Order.objects.get(email="test1@test.com")
        order_serialized = OrderSerializer(order)

        #update quantity
        response = self.client.put(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        s = "Out of stock"
        self.assertIn(s, str(response.data))

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 299)# inventory unchanged

class DeleteSingleOrderTest(APITestCase):
    """ Test module for deleting an existing inventory record """

    def setUp(self):
        setUpInventory(self)
        order_data1 = {"email": "test1@test.com",
                      "ordered_items": [
                          
                          {
                              "quantity": 2,
                              "product": 2
                          },
                          {
                              "quantity": 1,
                              "product": 1
                          }
                      ]}
        order_data2 = {"email": "test2@test.com",
                      "ordered_items": [
                          {
                              "quantity": 1,
                              "product": 1
                          }
                      ]}

        #create 2 orders
        self.client.post(reverse("orders:order-list"), data=json.dumps(order_data1),
                                    content_type='application/json')
        self.client.post(reverse("orders:order-list"), data=json.dumps(order_data2),
                                    content_type='application/json')
    def test_remove_order_item(self):
            order = Order.objects.get(email="test1@test.com")
            order_serialized = OrderSerializer(order)

            ordered_item = order.ordered_items.first()
            response = self.client.delete(
            reverse("orders:order_item", kwargs={'order_id': order.pk}), data=json.dumps({"item_id": ordered_item.pk}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            len_ordered_items = len(Order.objects.get(email="test1@test.com").ordered_items.all())
            self.assertEqual(len_ordered_items, 1) #only one ordered_item left in this order
   
    def test_post_order_item(self):
            order = Order.objects.get(email="test1@test.com")
            order_serialized = OrderSerializer(order)

            ordered_item = order.ordered_items.first()

            response = self.client.post(
            reverse("orders:order_item", kwargs={'order_id': order.pk}), data=json.dumps({"product": 3, "quantity":2}), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Inventory.objects.get(id=self.third.id).quantity, 298)
            
            len_ordered_items = len(Order.objects.get(email="test1@test.com").ordered_items.all())
            self.assertEqual(len_ordered_items, 3) #added one ordered item to the order



    def test_valid_delete_order(self):

        order = Order.objects.get(email="test1@test.com")
        order_serialized = OrderSerializer(order)

        response = self.client.delete(
            reverse("orders:order-detail", kwargs={'pk': order.__dict__.get("id")}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        inventory = Inventory.objects.get(pk=self.first.pk)
        inventory_serialized = InventorySerializer(inventory)
        self.assertEqual(inventory_serialized.data.get("quantity"), 299)
        #before delete order, the product quantity was 298, only order with email test2@test.com exists

    def test_invalid_delete_order(self):
        response = self.client.delete(
            reverse("orders:order-detail", kwargs={'pk': 1000}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

   


