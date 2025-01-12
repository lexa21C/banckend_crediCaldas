from rest_framework import serializers
from django.contrib.auth.models import User
from gestion.models import Cuota, Credito
# Serializer para Cuota
class CuotaDetalleSerializer(serializers.HyperlinkedModelSerializer):
    
    credito = serializers.PrimaryKeyRelatedField(queryset=Credito.objects.all())  # Muestra información del crédito asociado

    class Meta:
        model = Cuota
        depth = 3
        fields = ['url','id', 'credito', 'fecha_pago', 'fecha_pagada', 'valor', 'valor_cancelado', 'estado','num_cuotas']