from django.forms.fields import DecimalField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField, DecimalField, ModelSerializer, SerializerMethodField
from core.models import Compra
from core.models import Compra, ItensCompra

class ItensCompraSerializer(ModelSerializer):
    titulo =CharField(source='livro.titulo', read_only=True)
    editora = CharField(source='livro.editora.nome', read_only=True)
    preco = DecimalField(
        source='livro.preco', 
        max_digits=7, 
        decimal_places=2, 
        read_only=True)
    
    capa = CharField(source='livro.capa.url', read_only=True)
    
    class Meta:
        model = ItensCompra
        fields = ('id', 'titulo', 'editora', 'quantidade', 'preco', 'capa')

class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True) # inclua essa linha 
    status = CharField(source='get_status_display', read_only=True) # inclua essa linha
    itens = ItensCompraSerializer(many=True, read_only=True)
    

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'itens')
        

        
        
