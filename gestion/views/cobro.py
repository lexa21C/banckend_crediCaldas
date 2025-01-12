from gestion.models import Cobro
from rest_framework import viewsets
from gestion.serializers.cobro import CobroSerializer
class CobroViewSet(viewsets.ModelViewSet):
    queryset = Cobro.objects.all()
    serializer_class = CobroSerializer