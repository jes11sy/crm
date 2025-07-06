from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TipZayavki, Zayavka, ZayavkaFile
from .serializers import TipZayavkiSerializer, ZayavkaSerializer, ZayavkaFileSerializer

# Create your views here.

class TipZayavkiViewSet(viewsets.ModelViewSet):
    queryset = TipZayavki.objects.all()
    serializer_class = TipZayavkiSerializer

class ZayavkaViewSet(viewsets.ModelViewSet):
    queryset = Zayavka.objects.all()
    serializer_class = ZayavkaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['master_id', 'user_id', 'status', 'created_at']
    ordering_fields = ['created_at', 'updated_at']
    search_fields = ['title', 'description']

class ZayavkaFileViewSet(viewsets.ModelViewSet):
    queryset = ZayavkaFile.objects.all()
    serializer_class = ZayavkaFileSerializer
