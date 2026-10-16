from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_email:
            if user_by_username != user_by_email:
                raise serializers.ValidationError(
                    'Username и email принадлежат разным пользователям.'
                )
        elif user_by_username and not user_by_email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        elif user_by_email and not user_by_username:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
