from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TipTranzakcii, Tranzakciya, Payout
from .serializers import TipTranzakciiSerializer, TranzakciyaSerializer, PayoutSerializer

# Create your views here.

class TipTranzakciiViewSet(viewsets.ModelViewSet):
    queryset = TipTranzakcii.objects.all()
    serializer_class = TipTranzakciiSerializer

class TranzakciyaViewSet(viewsets.ModelViewSet):
    queryset = Tranzakciya.objects.all()
    serializer_class = TranzakciyaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['master_id', 'user_id', 'status', 'created_at', 'zayavka_id']
    ordering_fields = ['created_at', 'updated_at', 'amount']
    search_fields = ['description']

class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['master_id', 'status', 'payment_method', 'created_at']
    ordering_fields = ['created_at', 'updated_at', 'amount']
    search_fields = ['description']
