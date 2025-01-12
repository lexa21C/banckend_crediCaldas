from rest_framework import serializers
from django.contrib.auth.models import User
from gestion.models import Cuota, Credito

# Serializer para Cuota
class CuotaSerializer(serializers.HyperlinkedModelSerializer):
    credito = serializers.PrimaryKeyRelatedField(queryset=Credito.objects.all())  # Muestra información del crédito asociado

    class Meta:
        model = Cuota
        fields = ['url', 'id', 'credito', 'fecha_pago', 'fecha_pagada', 'valor', 'valor_cancelado', 'estado','num_cuotas']

