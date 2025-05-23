from rest_framework import serializers
from gestion.models import Credito, Cuota, Cobro
from datetime import timedelta
from decimal import Decimal
from gestion.serializers.getCreditos import CreditoDetailSerializer
import holidays 
class CreditoSerializer(serializers.HyperlinkedModelSerializer):
    cuotas = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='cuota-detail'
    )

    class Meta:
        model = Credito
        fields = [
            'url', 'id', 'cliente', 'fecha_prestamo', 'saldo', 'prestamo',
            'forma_pago', 'numero_cuotas', 'estado', 'cuotas_atrasadas',
            'cuotas', 'num_cuotas_pagadas'
        ]

    def obtener_festivos_colombia(self):
        """
        Retorna un conjunto con los días festivos de Colombia para el año especificado.
        """
        festivos_colombia = holidays.CO(years=2025)

        return set(festivos_colombia.keys())  # Devuelve las fechas festivas en un conjunto

    def es_dia_valido(self, fecha, festivos):
        """
        Verifica si un día es válido (ni domingo ni festivo).
        """
        return fecha.weekday() != 6 and fecha not in festivos  # Excluye domingos y festivos

    def generar_cuotas(self, credito, festivos):
        """
        Genera las cuotas basadas en la forma de pago, comenzando de acuerdo a la frecuencia
        especificada (diaria, semanal, quincenal o mensual) y respetando días válidos.
        """
        # Inicializar la fecha de la primera cuota dependiendo de la forma de pago
        if credito.forma_pago == 'diario':
            fecha_actual = credito.fecha_prestamo + timedelta(days=1)
        elif credito.forma_pago == 'semanal':
            fecha_actual = credito.fecha_prestamo + timedelta(weeks=1)
        elif credito.forma_pago == 'quincenal':
            fecha_actual = credito.fecha_prestamo + timedelta(days=15)
        elif credito.forma_pago == 'mensual':
            fecha_actual = credito.fecha_prestamo + timedelta(days=30)
        else:
            raise ValueError("Forma de pago no válida")

        # Ajustar al siguiente día válido si es necesario
        while not self.es_dia_valido(fecha_actual, festivos):
            fecha_actual += timedelta(days=1)

        valor_cuota = credito.saldo / credito.numero_cuotas  # Valor de cada cuota

        for numero_cuota in range(1, credito.numero_cuotas + 1):
            # Crear la cuota
            Cuota.objects.create(
                credito=credito,
                fecha_pago=fecha_actual,
                valor=valor_cuota,
                valor_cancelado=Decimal('0.00'),
                num_cuotas=numero_cuota,  # Asignar el número de la cuota
            )

            # Incrementar la fecha según la forma de pago
            if credito.forma_pago == 'diario':
                fecha_actual += timedelta(days=1)
                while not self.es_dia_valido(fecha_actual, festivos):
                    fecha_actual += timedelta(days=1)
            elif credito.forma_pago == 'semanal':
                fecha_actual += timedelta(weeks=1)
            elif credito.forma_pago == 'quincenal':
                fecha_actual += timedelta(days=15)
            elif credito.forma_pago == 'mensual':
                fecha_actual += timedelta(days=30)

    def create(self, validated_data):
        """
        Sobrescribe el método de creación para ajustar el saldo, generar cuotas
        y actualizar el capital en el modelo Cobro.
        """
        # Aumentar el monto del préstamo en un 20% (entero)
        prestamo_original = validated_data['prestamo']
        validated_data['prestamo'] = int(prestamo_original * 1.20)

        # Asignar al saldo el mismo valor que el préstamo
        validated_data['saldo'] = validated_data['prestamo']

        # Crear el objeto Crédito
        credito = Credito.objects.create(**validated_data)

        
        festivos = self.obtener_festivos_colombia()
        # Generar cuotas
        self.generar_cuotas(credito, festivos)

        # Actualizar el modelo Cobro
        try:
            cobro = Cobro.objects.first()  # Recuperar el primer registro de Cobro
            if cobro:
                cobro.capital_disponible -= prestamo_original
                cobro.capital_prestado += validated_data['prestamo']
                cobro.save()
        except Cobro.DoesNotExist:
            raise ValueError("No se encontró un objeto Cobro para actualizar.")

        return credito
    def update(self, instance, validated_data):
        """
        Edita un crédito existente, eliminando las cuotas antiguas y generando nuevas.
        """
        if 'prestamo' in validated_data and validated_data['prestamo'] != instance.prestamo:
            nuevo_prestamo = int(validated_data['prestamo'] * 1.20)
            validated_data['prestamo'] = nuevo_prestamo
            validated_data['saldo'] = nuevo_prestamo

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.cuotas.all().delete()

        # Obtener festivos correctamente
        festivos = self.obtener_festivos_colombia()
        self.generar_cuotas(instance, festivos)

        return instance