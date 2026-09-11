from django.forms.fields import DecimalField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ( CharField, CurrentUserDefault,DateTimeField, HiddenField, ModelSerializer,SerializerMethodField, ValidationError,)
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
        fields = ('livro', 'quantidade', 'preco', 'total')  # mudou

    def get_total(self, instance):
        return instance.quantidade * instance.preco
        
class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco')  # mudou

    def validate_quantidade(self, quantidade):
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior do que zero.')
        return quantidade

    def validate(self, item):
        if item['quantidade'] > item['livro'].quantidade:
            raise ValidationError('Quantidade de itens maior do que a quantidade em estoque.')
        return item
    
class CompraCreateUpdateSerializer(ModelSerializer):
    usuario = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item in itens:
            item['preco'] = item['livro'].preco # preço do livro no momento da compra
            ItensCompra.objects.create(compra=compra, **item)
        compra.save()
        return compra

    
    @transaction.atomic
    def update(self, compra, validated_data):
        itens = validated_data.pop('itens')
        if itens:
            compra.itens.all().delete()
            for item in itens:
                item['preco'] = item['livro'].preco  # grava o preço histórico
                ItensCompra.objects.create(compra=compra, **item)
        compra.save()
        return super().update(compra, validated_data)

class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True) # inclua essa linha 
    data = DateTimeField(read_only=True) # novo campo
    status = CharField(source='get_status_display', read_only=True) # inclua essa linha
    itens = ItensCompraSerializer(many=True, read_only=True)
    

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'data', 'itens') # modificado

class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'preco', 'livro')  # mudou
        depth = 1

    

class CompraListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensCompraListSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')        

