from rest_framework import viewsets
from .models import PriceRecord
from .serializers import PriceRecordSerializer

class PriceRecordViewSet(viewsets.ModelViewSet):
    queryset = PriceRecord.objects.all()
    serializer_class = PriceRecordSerializer
