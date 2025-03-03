from rest_framework import viewsets
from gestion.models import Cliente
from gestion.serializers.cliente import ClienteSerializer
from gestion.serializers.detalleCliente import ClienteDetalleSerializer
from rest_framework import status
from rest_framework.response import Response


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def update(self, request, *args, **kwargs):
        # Obtener el objeto Cliente que se va a actualizar
        cliente = self.get_object()
        nuevo_num_ruta = request.data.get('num_ruta')

        # Si el número de ruta ha cambiado, realizamos la lógica de ajuste
        if nuevo_num_ruta and cliente.num_ruta != nuevo_num_ruta:
            # Buscar clientes cuya ruta es mayor o igual al nuevo número de ruta
            clientes_con_ruta = Cliente.objects.filter(num_ruta__gte=nuevo_num_ruta).exclude(id=cliente.id)
            for cliente_ajustado in clientes_con_ruta:
                cliente_ajustado.num_ruta += 1
                cliente_ajustado.save()

            # Actualizar el número de ruta del cliente actual
            cliente.num_ruta = nuevo_num_ruta
            cliente.save()

        # Proceder con la actualización normal utilizando el serializer
        serializer = self.get_serializer(cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
