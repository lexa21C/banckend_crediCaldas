from rest_framework import viewsets
from gestion.models import Perfil
from gestion.serializers.perfil import PerfilSerializer
from rest_framework.exceptions import ValidationError

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer

    def perform_create(self, serializer):
        # Asegurarte de que no se cree un perfil duplicado
        usuario = serializer.validated_data.get('usuario')
        if Perfil.objects.filter(usuario=usuario).exists():
            raise ValidationError({"usuario": "Este usuario ya tiene un perfil asociado."})
        serializer.save()
