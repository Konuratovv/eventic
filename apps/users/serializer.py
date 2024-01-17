from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.profiles.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import ValidationError

from apps.users.models import CustomUser


class RegisterSerializer(ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'confirm_password',
        ]

    def validate_password(self, value):
        request = self.context.get('request')
        try:
            validate_password(value, request.user)
        except ValidationError as e:
            raise AuthenticationFailed(detail=e, code='invalid_password')
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise AuthenticationFailed('Password did not match')
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['code', 'email']


class SendCodeSerializer(serializers.Serializer):
    pass
