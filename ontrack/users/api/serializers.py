from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }

    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        print(str(refresh.access_token))

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
