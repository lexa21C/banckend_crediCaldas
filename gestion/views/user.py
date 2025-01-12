from rest_framework import viewsets
from django.contrib.auth.models import User
from gestion.serializers.user import UserSerializer
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]  # Asegúrate de que solo los usuarios autenticados puedan usar esta vista.
