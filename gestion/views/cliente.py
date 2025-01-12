from rest_framework import viewsets
from gestion.models import Cliente
from gestion.serializers.cliente import ClienteSerializer
from gestion.serializers.detalleCliente import ClienteDetalleSerializer

# ViewSet para Rol
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
