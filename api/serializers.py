from django.db import models
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model


# grab the user model

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password')