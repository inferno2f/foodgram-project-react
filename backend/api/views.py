from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api.models import Tag, Recipe
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CreateUserSerializer,
    TagSerializer,
    RecipeSerializer
)
from users.models import CustomUser


class UserViewSet(ModelViewSet):
    """Viewset for all user-related opertations. Uses djoser endpoints"""
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=('get',), detail=False, permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=request.user.id)
        if request.method == 'GET':
            serializer = CreateUserSerializer(user, many=False)
            return Response(serializer.data)
    # TODO: добавить сериализатор для просмотра информации


class TagViewSet(ViewSet):
    """
    Provides `GET` and `LIST` methods for all users.
    Tags can only be edited via admin panel.
    """

    def list(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('get', 'delete'),
            detail=True, permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            return Response(
                recipe.favorite.add(request.user),
                status.HTTP_202_ACCEPTED)
        elif request.method == 'DELETE':
            return Response(
                recipe.favorite.remove(request.user),
                status.HTTP_202_ACCEPTED)
    # FIXME: добавить "укороченный" сериализатор рецепта и вывести serializer.data
