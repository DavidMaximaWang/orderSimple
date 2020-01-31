import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Inventory
from .serializers import InventorySerializer

   
class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_inventory(data):
        #data attrs include name, description, price, quantity
        #{"name":"product1", "description":"gooddddd", "price":322.22, "quantity":200}
        Inventory.objects.create(**data)

    def setUp(self):
        # add test data
        data = {"name": "test_product0", "description": "gooddddd",
                "price": 322.22, "quantity": 200}
        self.create_inventory(data)
        data["quantity"]=201
        data["name"]="test_product1"
        self.create_inventory(data)



class GetAllInventory(BaseViewTest):

    def test_get_all_inventories(self):
        expected  = Inventory.objects.all()
        response = self.client.get(reverse("inventories:inventories-list"))

       
        serialized = InventorySerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleInventoryTest(APITestCase):

    def setUp(self):
        
        self.first = Inventory.objects.create(
            name='test_product100', description="gooddddd", price=322.22, quantity=300)

    def test_get_valid_single_inventory(self):
        expected = Inventory.objects.first()
        response = self.client.get(reverse("inventories:inventories-detail", kwargs={"slug":self.first.slug}))

        first = Inventory.objects.get(pk=self.first.pk)
        serializer = InventorySerializer(first)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_inventory(self):
        #test invalid slug
        response = self.client.get(reverse("inventories:inventories-detail", kwargs={"slug":"aaa"}))

        obj = {
            "errors": {
                "detail": "Not found."
            }
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, obj)


class CreateNewInventoryTest(APITestCase):
    
    def setUp(self):
        self.valid_payload={
            'name':'test_product100', 'description':"gooddddd", 'price':322.22
        }
        

    def test_create_valid_single_inventory(self):
        response = self.client.post(reverse("inventories:inventories-list"),
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json'
                                    )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse("inventories:inventories-list"),
                                    data=json.dumps(self.valid_payload),
                                    content_type='application/json'
                                    )
        #can not have duplicate inventory name
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

class UpdateSingleInventoryTest(APITestCase):
    """ Test module for updating an existing inventory record """

    def setUp(self):
        self.first = Inventory.objects.create(
            name='product100', description="good product", price=23.99)
        self.second = Inventory.objects.create(
            name='product101', description="good product", price=23.99)
        self.valid_payload = {
            'description': "very good product",
            'quantity': 100,
        }
        self.invalid_payload = {
            'price': 9999.99,
        }#max 5 digits for price

    def test_valid_update_inventory(self):
        self.assertEqual(self.first.quantity, 1)
        response = self.client.put(
            reverse("inventories:inventories-detail", kwargs={'slug': self.first.slug}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.data.get('quantity', None), 100)
        self.assertEqual(response.data.get('description', None), "very good product")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_inventory(self):
        response = self.client.put(
            reverse("inventories:inventories-detail", kwargs={'slug': self.first.slug}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteSingleInventoryTest(APITestCase):
    """ Test module for deleting an existing inventory record """

    def setUp(self):
        self.first = Inventory.objects.create(
            name='product100', description="good product", price=23.99)

    def test_valid_delete_inventory(self):
        response = self.client.delete(
            reverse("inventories:inventories-detail", kwargs={'slug': self.first.slug}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_inventory(self):
        response = self.client.delete(
            reverse("inventories:inventories-detail", kwargs={'slug': self.first.slug+"aaa"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
