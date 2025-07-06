from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import TipTranzakcii, Tranzakciya, Payout

# Create your tests here.

class TipTranzakciiAPITest(APITestCase):
    def test_create_list_tiptranzakcii(self):
        url = reverse('tiptranzakcii-list')
        data = {'name': 'Тестовый тип', 'description': 'Описание типа'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class TranzakciyaAPITest(APITestCase):
    def setUp(self):
        self.tip = TipTranzakcii.objects.create(name='Тип транзакции', description='Описание')
    def test_create_list_tranzakciya(self):
        url = reverse('tranzakcii-list')
        data = {
            'tip_id': self.tip.id, 
            'description': 'Тестовая транзакция', 
            'user_id': 1, 
            'master_id': 1, 
            'amount': 100.50, 
            'status': 'pending'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

class PayoutAPITest(APITestCase):
    def test_create_list_payout(self):
        url = reverse('payouts-list')
        data = {
            'master_id': 1, 
            'description': 'Тестовая выплата', 
            'amount': 500.00, 
            'status': 'pending', 
            'payment_method': 'bank'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
