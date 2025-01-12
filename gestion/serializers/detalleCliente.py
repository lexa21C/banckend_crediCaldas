from rest_framework import serializers
from django.contrib.auth.models import User
from gestion.models import Cliente
from rest_framework.permissions import IsAuthenticated
class ClienteDetalleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cliente
        fields = ['url','id', 'nombre_completo', 'cliente_id','num_ruta','direccion', 'direccion_otra', 'telefono','barrio','referencia']
    
        #permission_classes = [IsAuthenticated]  # Permitir solo a usuarios autenticados