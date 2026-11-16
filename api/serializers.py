from .models import Ticket
from rest_framework import serializers

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['author']

    def validate(self, attrs):
        if attrs.get('priority') == 'CRITICAL':
            description = attrs.get('description' , '')
            if len(description) <30:
                raise serializers.ValidationError({
                    'description':'чувак в тенбе занажто короткий дескріпшн'
                })
        return attrs