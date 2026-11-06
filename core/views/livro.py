from rest_framework import status
from core.views.user import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import OpenApiResponse, extend_schema
from django.db.models import Q, Sum

from core.models import Livro, Compra
from core.serializers import LivroAlterarPrecoSerializer, LivroMaisVendidoSerializer, LivroRetrieveSerializer, LivroListSerializer, LivroSerializer, LivroAjustarEstoqueSerializer



class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer  # Seu serializer padrão

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['categoria__descricao', 'editora__nome']  # Campos para filtragem
    search_fields = ['titulo']  # Campos para busca textual


    def get_serializer_class(self):
            if self.action in {'list', 'retrieve'}:
                return LivroListSerializer
            elif self.action == 'retrieve':
                return LivroRetrieveSerializer
            return LivroSerializer
    
    @extend_schema(
        summary="Ajusta o estoque de um livro",
        description="Aumenta ou diminui o estoque; impede resultado negativo.",
        request=LivroAjustarEstoqueSerializer,
        responses={
            200: OpenApiResponse(
                response=None,
                description="Estoque ajustado com sucesso.",
                examples=[
                    {
                        "status": "Quantidade ajustada com sucesso",
                        "novo_estoque": 30
                    }
                ]
            ),
            400: OpenApiResponse(
                description="Erro de validação",
                examples=[
                    {"quantidade": "A quantidade em estoque não pode ser negativa."}
                ]
            ),
        },
        )
    @action(detail=True, methods=['post'])
    def ajustar_estoque(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAjustarEstoqueSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)

        quantidade_ajuste = serializer.validated_data['quantidade']
        livro.quantidade += quantidade_ajuste
        livro.save()

        return Response(
            {'status': 'Quantidade ajustada com sucesso', 'novo_estoque': livro.quantidade},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAlterarPrecoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        livro.preco = serializer.validated_data['preco']
        livro.save()

        return Response(
            {'detail': f'Preço do livro "{livro.titulo}" atualizado para {livro.preco}.'}, status=status.HTTP_200_OK
        ) 
    @extend_schema(
            summary="Lista os livros mais vendidos",
            description="Retorna os livros que venderam mais de 10 unidades.",
            responses={
                200: LivroMaisVendidoSerializer(many=True)
            },
        )
    
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        livros = Livro.objects.annotate(
            total_vendidos=Sum(
                'itens_compra__quantidade',
                filter=Q(itens_compra__compra__status=Compra.StatusCompra.FINALIZADO)
            )
        ).filter(total_vendidos__gt=10).order_by('-total_vendidos')

        serializer = LivroMaisVendidoSerializer(livros, many=True)

        if not serializer.data:
            return Response(
                {"detail": "Nenhum livro excedeu 10 vendas."},
                status=status.HTTP_200_OK
            )

        

        return Response(serializer.data, status=status.HTTP_200_OK) 

    


    
    
    
