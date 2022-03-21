from django.shortcuts import get_object_or_404
from rest_framework import permissions
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(methods=('get', 'post'), detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeSerializer(recipe)
        if serializer.is_valid():
            if request.user not in recipe.favorite.all():
                recipe.favorite.add(request.user)
            elif request.user in recipe.favorite.all():
                recipe.favorite.remove(request.user)
            serializer.save()
            return Response(serializer.data)
    # FIXME: разобраться с PATCH реквестом. 'Request' object has no attribute 'obj'
