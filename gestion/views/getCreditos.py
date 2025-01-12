from rest_framework import viewsets
from gestion.models import Credito
from gestion.serializers.getCreditos import CreditoDetailSerializer
class CreditoDetailViewSet(viewsets.ModelViewSet):
    queryset = Credito.objects.all()
    serializer_class = CreditoDetailSerializer