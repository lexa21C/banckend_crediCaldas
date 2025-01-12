from rest_framework import serializers
from gestion.models import Credito, Cuota
from datetime import timedelta
from decimal import Decimal

class CreditoDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Credito
        depth = 3
        fields = [
            'id', 'cliente', 'fecha_prestamo', 'saldo', 'prestamo',
            'forma_pago', 'numero_cuotas', 'estado', 
            'cuotas_atrasadas', 'cuotas', 'num_cuotas_pagadas'
        ]