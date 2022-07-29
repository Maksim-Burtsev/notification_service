import json

from django.test import TestCase

from main.models import Client


class MainAPITestCase(TestCase):

    def setUp(self) -> None:
        for i in range(10):
            client = Client.objects.create(
                phone_number=f'7888123231{i}',
                operator_code='888',
                time_zone='utc'
            )
        return super().setUp()

    def test_add_client(self):
        data = {'phone_number':'78881232333', 'operator_code':'888', 'time_zone':'utc'}

        response = self.client.post('/api/add_client', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id":11})

    def test_cliet_invalid_number(self):
        data = {'phone_number':'12fsafqrwq', 'operator_code':'888', 'time_zone':'utc'}

        response = self.client.post('/api/add_client', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_update_client(self):

        client = Client.objects.first()
        data = {'phone_number':'78881232333', 'operator_code':'888', 'time_zone':'utc'}

        response = self.client.put(f'/api/update_client/{client.id}', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_wrong_update_client(self):
        client = Client.objects.first()

        data = {'phone_number':'78881232311', 'operator_code':'888', 'time_zone':'utc'}

        response = self.client.put(f'/api/update_client/{client.id}', data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_delete_client(self):
        client = Client.objects.last()
        print(client.id)

        response = self.client.delete(f"/api/delete_client/{client.id}")
        
        self.assertEqual(response.status_code, 200)

    def test_delete_404(self):

        response = self.client.delete(f"/api/delete_client/1")

        self.assertEqual(response.status_code, 404)
