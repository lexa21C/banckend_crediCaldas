from rest_framework import serializers
from gestion.models import Gasto, Cobro

class GastoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gasto
        fields = ['id', 'nombre', 'valor', 'fecha']

    def create(self, validated_data):
        # Aumentar el monto del préstamo en un 20% (entero)
        valor_gasto = validated_data['valor']
        print(valor_gasto)
        # Actualizar el modelo Cobro
        try:
            cobro = Cobro.objects.first()  # Recuperar el primer registro de Cobro
            if cobro:
                cobro.capital_disponible -= valor_gasto
                cobro.save()
        except Cobro.DoesNotExist:
            raise ValueError("No se encontró un objeto Cobro para actualizar.")

        # Crear y devolver la instancia del gasto
        return Gasto.objects.create(**validated_data)
