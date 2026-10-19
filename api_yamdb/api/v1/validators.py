from rest_framework import serializers


class UsernameValidatorMixin:
    """Миксин для запрета username 'me'."""

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено.'
            )
        return value
