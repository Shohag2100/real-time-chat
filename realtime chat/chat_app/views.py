from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
