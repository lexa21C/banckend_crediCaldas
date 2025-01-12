from rest_framework import viewsets
from gestion.models import Gasto
from gestion.serializers.gastos import GastoSerializer

class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer