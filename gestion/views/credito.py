from rest_framework import viewsets
from gestion.models import Credito, Cuota
from gestion.serializers.getCreditos import  CreditoDetailSerializer
from gestion.serializers.credito import CreditoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from django.db.models import Q

class CreditoViewSet(viewsets.ModelViewSet):
    queryset = Credito.objects.all()
    serializer_class = CreditoSerializer

    def get_serializer_class(self):
        # Si la acción es 'retrieve' o 'buscar_por_fecha', usa el serializador con depth=3
        if self.action in ['retrieve', 'buscar_por_fecha']:
            return CreditoDetailSerializer
        return CreditoSerializer

    @action(detail=False, methods=['get'])
    def buscar_por_fecha(self, request):
        # Obtener la fecha de los parámetros de la solicitud
        fecha_param = request.query_params.get('fecha', None)
        if not fecha_param:
            return Response({"error": "El parámetro 'fecha' es obligatorio."}, status=400)

        try:
            fecha = parse_date(fecha_param)
            if not fecha:
                raise ValueError("Formato de fecha no válido.")
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # Filtrar las cuotas con la fecha dada y estado activo o pendiente
        cuotas_filtradas = Cuota.objects.filter(
            Q(fecha_pago=fecha, estado='activo') | Q(estado='pendiente')
        ).values_list('credito_id', flat=True)  # Obtener IDs de los créditos relacionados

        # Obtener los créditos relacionados
        creditos_filtrados = Credito.objects.filter(
            id__in=cuotas_filtradas
        ).distinct()

        # Serializar los resultados con depth=3
        serializer = self.get_serializer(creditos_filtrados, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def buscarCredito(self, request, pk=None):
        """
        Busca un crédito por ID y filtra sus cuotas por fecha y estado,
        mostrando datos relacionados con depth=3.
        """
        # Obtener la fecha del argumento de la solicitud
        fecha_param = request.query_params.get('fecha', None)
        if not fecha_param:
            return Response({"error": "El parámetro 'fecha' es obligatorio."}, status=400)

        try:
            fecha = parse_date(fecha_param)
            if not fecha:
                raise ValueError("Formato de fecha no válido.")
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # Filtrar el crédito por ID
        try:
            credito = Credito.objects.get(id=pk)
        except Credito.DoesNotExist:
            return Response({"error": "Crédito no encontrado."}, status=404)

        # Filtrar las cuotas del crédito que cumplen las condiciones
        cuotas_filtradas = credito.cuotas.filter(
            Q(fecha_pago=fecha, estado='activo') | Q(estado='pendiente')
        )

        # Usar el serializador con depth=3 y pasar el request en el contexto
        serializer_class = CreditoDetailSerializer
        serializer = serializer_class(credito, context={'request': request})  # Pasar el request en el contexto

        # Incluir las cuotas filtradas manualmente en la respuesta
        data = serializer.data

        data['cuotas_filtradas'] = [
            {
                "id": cuota.id,
                "fecha_pago": cuota.fecha_pago,
                "valor": cuota.valor,
                "valor_cancelado": cuota.valor_cancelado,
                "fecha_pagada": cuota.fecha_pagada,
                "estado": cuota.estado,
                "credito": cuota.credito.id,  # Convertir el objeto Credito a su ID
                "num_cuotas":cuota.num_cuotas
            }
            for cuota in cuotas_filtradas
        ]

        return Response(data)
    @action(detail=False, methods=['get'])
    def creditoPorCliente(self, request):
        """
        Endpoint para obtener los IDs de los créditos activos de un cliente.
        """
        cliente_id = request.query_params.get('cliente_id', None)
        if not cliente_id:
            return Response({"error": "El parámetro 'cliente_id' es obligatorio."}, status=400)

        try:
            # Filtrar créditos por cliente y estado activo
            creditos = Credito.objects.filter(cliente_id=cliente_id, estado='activo')
            if not creditos.exists():
                return Response({"error": "No se encontraron créditos activos para el cliente proporcionado."}, status=404)

            # Extraer únicamente los IDs
            creditos_ids = creditos.values_list('id', flat=True)
        except Exception as e:
            return Response({"error": f"Ocurrió un error: {str(e)}"}, status=400)

        return Response(list(creditos_ids))