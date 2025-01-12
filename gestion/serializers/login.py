from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Agregar información personalizada al token
        data['user'] = self.user
        #data['id'] = self.user.email
        #data['full_name'] = f"{self.user.first_name} {self.user.last_name}"
        return data
