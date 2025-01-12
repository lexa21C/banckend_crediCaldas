from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from gestion.serializers.login import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from gestion.serializers.user import UserSerializer
from django.contrib.auth.models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Obtener los tokens
        refresh_token = response.data.get('refresh')
        access_token = response.data.get('access')

        # Obtener los datos del usuario
        user = User.objects.get(username=request.data['username'])
        user_data = UserSerializer(user, context={'request': request}).data  # Agregar el contexto aquí
        
        # Devolver los tokens junto con los datos del usuario
        return Response({
            'refresh': refresh_token,
            'access': access_token,
            'user': user_data
        })


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "¡Acceso permitido!", "user": request.user.username})
