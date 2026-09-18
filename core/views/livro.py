from rest_framework import status
from core.views.user import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema

from core.models import Livro
from core.serializers import LivroAlterarPrecoSerializer, LivroRetrieveSerializer, LivroListSerializer, LivroSerializer

class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.order_by('titulo')
    serializer_class = LivroSerializer

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return LivroListSerializer
        elif self.action == 'retrieve':
            return LivroRetrieveSerializer
        return LivroSerializer
    
    @extend_schema(
            request=LivroAlterarPrecoSerializer,
            responses={200: None},
            description="Altera o preço de um livro específico.",
            summary="Alterar preço do livro",
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
    
    
