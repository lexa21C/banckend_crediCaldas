from rest_framework import serializers
from django.contrib.auth.models import User
from gestion.models import Perfil
# Serializer para Perfil
class PerfilSerializer(serializers.HyperlinkedModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Perfil
        fields = ['id', 'rol', 'usuario']

    def validate_usuario(self, value):
        if Perfil.objects.filter(usuario=value).exists():
            raise serializers.ValidationError("Este usuario ya tiene un perfil asociado.")
        return value
