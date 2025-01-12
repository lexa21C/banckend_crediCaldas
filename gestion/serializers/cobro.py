from gestion.models import Cobro
from rest_framework import serializers
class CobroSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cobro
        fields = ['id', 'usuario', 'capital_inicial', 'capital_prestado', 'capital_cancelado', 'capital_disponible']
