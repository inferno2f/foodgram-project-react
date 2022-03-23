from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api.models import Ingredient, Recipe, Tag
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (ChangePasswordSerializer, CreateUserSerializer,
                             FavoriteRecipeSerializer, GetUserSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer)
from users.models import CustomUser


class UserViewSet(ModelViewSet):
    """Viewset for all user-related opertations. Uses djoser endpoints"""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return GetUserSerializer

    @action(methods=('get',),
            detail=False, permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """ Quick access to user's peronal profile via /me endpoint """
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = CreateUserSerializer(user, many=False)
        return Response(serializer.data)

    @action(methods=('post',),
            detail=False, permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        """ Provides a way to change a password """
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.data.get('current_password')
            if not user.check_password(current_password):
                return Response({'old_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('tag',)
    ordering = ('-id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        """ Add recipe to favorites """
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteRecipeSerializer(recipe)

        if request.method == 'GET':
            recipe.favorite.add(request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.favorite.remove(request.user),
            return Response(status.HTTP_204_NO_CONTENT)

    @action(methods=('get', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """ Add recipe to shopping cart """
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteRecipeSerializer(recipe)

        if request.method == 'GET':
            recipe.cart.add(request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.cart.remove(request.user),
            return Response(status.HTTP_204_NO_CONTENT)


class TagViewSet(ViewSet):
    """
    Provides `GET` and `LIST` methods for all users.
    Tags can only be added and edited via admin panel.
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


class IngredientViewSet(ViewSet):
    """
    Provides `GET` and `LIST` methods for all users.
    Ingredients can only be added and edited via admin panel.
    """

    def list(self, request):
        queryset = Ingredient.objects.all()
        serializer = IngredientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        ingredient = get_object_or_404(queryset, pk=pk)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)
