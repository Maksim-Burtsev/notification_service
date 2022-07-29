import json

from django.test import TestCase, override_settings

from main.models import Client, Mailing


class MainAPITestCase(TestCase):
    def setUp(self) -> None:
        for i in range(10):
            Client.objects.create(
                phone_number=f"7888123231{i}", operator_code="888", time_zone="utc"
            )
        Mailing.objects.create(
            start_time="2022-08-29T19:49:06.475Z",
            text="test",
            attribute="888",
            end_time="2023-07-29T19:49:06.475Z",
        )
        return super().setUp()

    def test_add_client(self):
        data = {
            "phone_number": "78881232333",
            "operator_code": "888",
            "time_zone": "utc",
        }

        response = self.client.post(
            "/api/add_client", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 11})

    def test_cliet_invalid_number(self):
        data = {
            "phone_number": "12fsafqrwq",
            "operator_code": "888",
            "time_zone": "utc",
        }

        response = self.client.post(
            "/api/add_client", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_client_invalid_code(self):
        data = {
            "phone_number": "12345678122",
            "operator_code": "abc",
            "time_zone": "utc",
        }

        response = self.client.post(
            "/api/add_client", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_update_client(self):

        client = Client.objects.first()
        data = {
            "phone_number": "78881232333",
            "operator_code": "888",
            "time_zone": "utc",
        }

        response = self.client.put(
            f"/api/update_client/{client.id}",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_wrong_update_client(self):
        client = Client.objects.first()

        data = {
            "phone_number": "78881232311",
            "operator_code": "888",
            "time_zone": "utc",
        }

        response = self.client.put(
            f"/api/update_client/{client.id}",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_client_404(self):

        data = {
            "phone_number": "78881232311",
            "operator_code": "888",
            "time_zone": "utc",
        }

        response = self.client.put(
            f"/api/update_client/1234",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_client(self):
        client = Client.objects.last()

        response = self.client.delete(f"/api/delete_client/{client.id}")

        self.assertEqual(response.status_code, 200)

    def test_delete_404(self):

        response = self.client.delete(f"/api/delete_client/1")

        self.assertEqual(response.status_code, 404)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_create_mailing(self):
        data = {
            "start_time": "2022-07-29T19:49:06.475Z",
            "text": "test",
            "attribute": "888",
            "end_time": "2023-07-29T19:49:06.475Z",
        }

        response = self.client.post(
            "/api/create_mailing",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_mailing(self):

        mailing = Mailing.objects.create(
            start_time="2022-07-29T19:49:06.475Z",
            text="test",
            attribute="888",
            end_time="2023-07-29T19:49:06.475Z",
        )

        response = self.client.delete(f"/api/delete_mailing/{mailing.id}")

        self.assertEqual(response.status_code, 200)

    def test_delete_mailing_404(self):
        response = self.client.delete("/api/delete_mailing/1000")

        self.assertEqual(response.status_code, 404)

    def test_update_mailing(self):

        mailing = Mailing.objects.first()

        data = {
            "start_time": "2022-07-29T19:49:06.475Z",
            "text": "test",
            "attribute": "888",
            "end_time": "2024-07-29T19:49:06.475Z",
        }

        response = self.client.put(
            f"/api/update_mailing/{mailing.id}",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_update_mailing_404(self):

        data = {
            "start_time": "2022-07-29T19:49:06.475Z",
            "text": "test",
            "attribute": "888",
            "end_time": "2024-07-29T19:49:06.475Z",
        }

        response = self.client.put(
            f"/api/update_mailing/12345",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_statistic(self):
        mailing = Mailing.objects.first()

        response = self.client.get(f"/api/detail_statics/{mailing.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_general_statistic(self):

        response = self.client.get(f"/api/general_statics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_detail_statistics2(self):
        data = {
            "start_time": "2022-07-29T19:49:06.475Z",
            "text": "test",
            "attribute": "888",
            "end_time": "2023-07-29T19:49:06.475Z",
        }

        response = self.client.post(
            "/api/create_mailing",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/api/detail_statics/{response.json()["id"]}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 10)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_general_statistic2(self):
        data = {
            "start_time": "2022-07-29T19:49:06.475Z",
            "text": "test",
            "attribute": "888",
            "end_time": "2023-07-29T19:49:06.475Z",
        }

        response = self.client.post(
            "/api/create_mailing",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/general_statics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[1],
            {
                "start_time": "2022-07-29T19:49:06.475Z",
                "text": "test",
                "attribute": "888",
                "end_time": "2023-07-29T19:49:06.475Z",
                "messages_count": {
                    "success": 10,
                    "wrong": 0,
                    "waiting": 0,
                    "trying": 0,
                    "total": 10,
                },
            },
        )
