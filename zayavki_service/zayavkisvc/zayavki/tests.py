from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import TipZayavki, Zayavka, ZayavkaFile
from django.contrib.auth import get_user_model

# Create your tests here.

class TipZayavkiAPITest(APITestCase):
    def test_create_list_tipzayavki(self):
        url = reverse('tipzayavki-list')
        data = {'name': 'Тестовый тип'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class ZayavkaAPITest(APITestCase):
    def setUp(self):
        self.tip = TipZayavki.objects.create(name='Тип')
    def test_create_list_zayavka(self):
        url = reverse('zayavki-list')
        data = {'tip_id': self.tip.id, 'description': 'Тестовая заявка', 'user_id': 1, 'master_id': 1, 'title': 'Тест', 'status': 'new'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class ZayavkaFileAPITest(APITestCase):
    def setUp(self):
        self.tip = TipZayavki.objects.create(name='Тип')
        self.zayavka = Zayavka.objects.create(tip=self.tip, description='Заявка', user_id=1, master_id=1, title='Тест', status='new')
    def test_create_list_zayavkafile(self):
        url = reverse('zayavkafiles-list')
        data = {'zayavka': self.zayavka.id, 'file': 'test.txt'}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
