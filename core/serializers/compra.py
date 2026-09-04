from django.forms.fields import DecimalField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import CharField, DecimalField, ModelSerializer, SerializerMethodField
from core.models import Compra
from core.models import Compra, ItensCompra
from django.db import transaction


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
        
class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade')

class CompraCreateUpdateSerializer(ModelSerializer):
    itens = ItensCompraCreateUpdateSerializer(many=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item_data in itens_data:
            ItensCompra.objects.create(compra=compra, **item_data)
        compra.save()
        return compra
    
    @transaction.atomic
    def update(self, compra, validated_data):
        itens_data = validated_data.pop('itens', None)
        if itens_data is not None:
            compra.itens.all().delete()
            for item_data in itens_data:
                ItensCompra.objects.create(compra=compra, **item_data)
        return super().update(compra, validated_data)

class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True) # inclua essa linha 
    status = CharField(source='get_status_display', read_only=True) # inclua essa linha
    itens = ItensCompraSerializer(many=True, read_only=True)
    

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'itens')

class CompraListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensCompraListSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')        

class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'livro')
        depth = 1