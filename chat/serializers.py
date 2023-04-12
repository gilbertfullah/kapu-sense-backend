from rest_framework import generics, serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model: Message
        fields: "__all__"
        
