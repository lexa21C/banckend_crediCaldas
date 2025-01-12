from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from gestion.models import Cuota, Credito, Cobro
from gestion.serializers.cuota import CuotaSerializer
from gestion.serializers.cuotaDetalles import CuotaDetalleSerializer

# ViewSet para Cuota
class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CuotaDetalleSerializer
        return CuotaSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Validar si la cuota ya está cancelada
        if instance.estado == 'cancelado':
            return Response(
                {"error": "No se puede editar una cuota que ya está cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        print(data)
        print(instance.valor_cancelado)
        # Obtener el valor cancelado y calcular el excedente
        valor_cancelado = int(data.get('valor_cancelado', instance.valor_cancelado))
        print(valor_cancelado)
        valor_actual = int(instance.valor)
        print(valor_actual)

        abono = valor_cancelado

        excedente = valor_cancelado - valor_actual if valor_cancelado > valor_actual else 0

        # Actualizar la cuota actual
        if excedente > 0:
            # Si hay excedente, ajustamos el valor_cancelado para completar esta cuota
            if instance.valor_cancelado > 0:
                data['valor'] += instance.valor_cancelado
                data['valor_cancelado'] = data['valor'] 
            else:
                data['valor_cancelado'] = valor_actual

            

            print(f"Después de guardar: valor_cancelado = {instance.valor_cancelado}")
            cuotas_pendientes = Cuota.objects.filter(
                credito=instance.credito,
                estado='activo',
                num_cuotas__gt=instance.num_cuotas
            ).order_by('num_cuotas')

            for cuota in cuotas_pendientes:
                if excedente <= 0:
                    break  # Si no hay excedente, salimos del bucle

                restante_cuota = cuota.valor - cuota.valor_cancelado  # Cuánto falta para pagar esta cuota

                if excedente >= restante_cuota:
                    # Si el excedente cubre completamente esta cuota
                    cuota.valor_cancelado = cuota.valor
                    excedente -= restante_cuota
                else:
                    # Si el excedente es menor que lo que falta por pagar en esta cuota
                    cuota.valor_cancelado += excedente
                    cuota.valor -= excedente
                    excedente = 0  # Agotamos el excedente

                cuota.save()  # Guardar los cambios en la cuota
        else:
            # Si no hay excedente, simplemente actualizamos el valor_cancelado
            if instance.valor_cancelado > 0:
                data['valor'] += instance.valor_cancelado
                data['valor_cancelado'] = data['valor'] 
                instance.valor_cancelado = valor_actual
            else:
                data['valor_cancelado'] = valor_actual

        previous_state = instance.estado  # Estado antes de la actualización

        # Validar y actualizar el objeto usando el serializer

        serializer = self.get_serializer(instance, data=data, partial=partial)
        print (serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Verificar si el estado de la cuota cambió a "pendiente"
        if previous_state != 'pendiente' and serializer.validated_data.get('estado') == 'pendiente':
            credito = instance.credito  # Obtener el crédito asociado
            credito.cuotas_atrasadas += 1  # Incrementar el contador de cuotas atrasadas
            credito.save()  # Guardar los cambios en el crédito
        else:
            credito = instance.credito  # Obtener el crédito asociado
            credito.saldo -= abono
            credito.save()  # Guardar los cambios en el crédito

        # Actualizar el modelo Cobro
        try:
            cobro = Cobro.objects.first()  # Recuperar el primer registro de Cobro
            if cobro:
                cobro.capital_disponible += abono
                cobro.capital_cancelado += abono
                cobro.capital_prestado -= abono
                cobro.save()
        except Cobro.DoesNotExist:
            raise ValueError("No se encontró un objeto Cobro para actualizar.")

        # Responder con los datos actualizados
        return Response(serializer.data, status=status.HTTP_200_OK)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from gestion.models import Cuota, Credito, Cobro
from gestion.serializers.cuota import CuotaSerializer
from gestion.serializers.cuotaDetalles import CuotaDetalleSerializer

# ViewSet para Cuota
class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CuotaDetalleSerializer
        return CuotaSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Validar si la cuota ya está cancelada
        if instance.estado == 'cancelado':
            return Response(
                {"error": "No se puede editar una cuota que ya está cancelada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # # Verificar si request.data es mutable y, si no, hacer una copia
        # if isinstance(request.data, dict):
        #     data = request.data.copy()  # Hacer una copia mutable si es un diccionario
        # else:
        #     data = dict(request.data)  # Si es QueryDict, convertirlo a diccionario y hacer copia
        data = request.data
        print(data)

        # Obtener el valor de 'valor_cancelado' del request
        valor_cancelado = int(data.get('valor_cancelado', 0))

        if valor_cancelado > 0:
            print("El valor cancelado es mayor a cero, procesando lógica avanzada.")
            # Calcular el excedente
            valor_actual = int(instance.valor)
            print(valor_actual)
            print(f"valor_cancelado: {valor_cancelado}, valor_actual: {valor_actual}")

            abono = valor_cancelado
            excedente = valor_cancelado - valor_actual if valor_cancelado > valor_actual else 0
            print(excedente)
            # Actualizar la cuota actual si hay excedente
            if excedente > 0:
                print('excedente')
                if instance.valor_cancelado > 0:
                    data['valor'] += instance.valor_cancelado
                    data['valor_cancelado'] = data['valor']
                else:
                    data['valor_cancelado'] = valor_actual
                    print(f"Después de guardar: valor_cancelado = {data['valor_cancelado']}")
                cuotas_pendientes = Cuota.objects.filter(
                    credito=instance.credito,
                    estado='activo',
                    num_cuotas__gt=instance.num_cuotas
                ).order_by('num_cuotas')

                for cuota in cuotas_pendientes:
                    if excedente <= 0:
                        break  # Si no hay excedente, salimos del bucle

                    restante_cuota = cuota.valor - cuota.valor_cancelado  # Cuánto falta para pagar esta cuota

                    if excedente >= restante_cuota:
                        cuota.valor_cancelado = cuota.valor
                        excedente -= restante_cuota
                    else:
                        cuota.valor_cancelado += excedente
                        cuota.valor -= excedente
                        excedente = 0  # Agotamos el excedente

                    cuota.save()  # Guardar los cambios en la cuota
            else:
                # Si no hay excedente, simplemente actualizamos el valor_cancelado
                if instance.valor_cancelado > 0:
                    print('instance.valor_cancelado > 0: ')
                    data['valor'] += instance.valor_cancelado
                    data['valor_cancelado'] = data['valor']
                    instance.valor_cancelado = valor_actual
                else:
                    print('instance.valor_cancelado else: ')
                    data['valor_cancelado'] = valor_actual
        if excedente==0:
            print ('valor ante',valor_cancelado)
            print('valor actual', valor_actual)
            if valor_cancelado < valor_actual:
                data['valor_cancelado'] = valor_cancelado
                data['valor'] -= data['valor_cancelado']    
                print('actualiza')  
                print(data)    
            else:
                data['valor_cancelado'] = valor_cancelado

        previous_state = instance.estado  # Estado antes de la actualización

        # Validar y actualizar el objeto usando el serializer
        serializer = self.get_serializer(instance, data=data, partial=partial)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Verificar si el estado de la cuota cambió a "pendiente"
        if previous_state != 'pendiente' and serializer.validated_data.get('estado') == 'pendiente':
            credito = instance.credito  # Obtener el crédito asociado
            credito.cuotas_atrasadas += 1  # Incrementar el contador de cuotas atrasadas
            credito.save()  # Guardar los cambios en el crédito
        
        credito = instance.credito  # Obtener el crédito asociado
        credito.saldo -= valor_cancelado
        credito.num_cuotas_pagadas += 1 
        if credito.saldo == 0:
            credito.estado = 'cancelado'
        credito.save()  # Guardar los cambios en el crédito

        # Actualizar el modelo Cobro
        try:
            cobro = Cobro.objects.first()  # Recuperar el primer registro de Cobro
            if cobro:
                cobro.capital_disponible += valor_cancelado
                cobro.capital_cancelado += valor_cancelado
                cobro.capital_prestado -= valor_cancelado
                cobro.save()
        except Cobro.DoesNotExist:
            raise ValueError("No se encontró un objeto Cobro para actualizar.")

        # Responder con los datos actualizados
        return Response(serializer.data, status=status.HTTP_200_OK)
