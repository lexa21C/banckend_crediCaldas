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
