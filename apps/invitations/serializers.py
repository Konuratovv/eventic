from rest_framework import serializers
from apps.invitations import Invitation

class InviSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'