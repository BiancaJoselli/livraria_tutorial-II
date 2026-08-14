from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField, ModelSerializer
from core.models import Compra

class CompraSerializer(ModelSerializer):
    class Meta:
        model = Compra
        fields = '__all__'

class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True) # inclua essa linha
    