import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter
from api.models import Ingredient, Recipe, Tag
from api.permissions import IsAuthorOrReadOnly, IsUserOrReadOnly
from api.serializers import (ChangePasswordSerializer, CreateRecipeSerialzer,
                             FavoriteRecipeSerializer, FollowSerializer,
                             GetRecipeSerializer, IngredientSerializer,
                             TagSerializer)
from foodgram.pagination import LimitPageNumberPaginator
from users.models import CustomUser, Follow


class CustomUserViewSet(UserViewSet):
    """Viewset for all user-related operations. Uses djoser endpoints"""
    @action(methods=('post',),
            detail=False, permission_classes=(IsUserOrReadOnly,))
    def set_password(self, request):
        """ Provides a way to change a password """
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        current_password = serializer.data.get('current_password')
        if not user.check_password(current_password):
            return Response({'old_password': ['Wrong password.']},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete'),
            detail=True, permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        user = get_object_or_404(CustomUser, username=request.user.username)
        author = get_object_or_404(CustomUser, id=id)
        serializer = FollowSerializer()
        follow = Follow.objects.all().filter(user=user, author=author)

        if request.method == 'POST':
            if not follow.exists():
                serializer = FollowSerializer(
                    Follow.objects.create(user=user, author=author))
                serializer.is_valid()
                serializer.save()
            return Response(
                serializer.data,
                status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if follow.exists():
                subscription = Follow.objects.filter(user=user, author=author)
                subscription.delete()
                return Response(
                    {'detail': 'subscription removed'},
                    status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'subscription doesn\'t exist'},
                status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """ Returns a list of all user subscriptions,
            including their recipes
        """
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('tags__slug',)
    ordering = ('-id')
    pagination_class = LimitPageNumberPaginator
    http_method_names = ('get', 'post', 'delete', 'patch')

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerialzer
        return GetRecipeSerializer

    def get_queryset(self):
        """ Get all recipes or filter them by property """
        queryset = self.queryset

        tags = self.request.query_params.get('tags')
        if tags:
            queryset = queryset.all().filter(tags__slug__in=tags.split(','))

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping == '1':
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping == '0':
            queryset = queryset.exclude(cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorite=user.id)
        if is_favorited == '0':
            queryset = queryset.exclude(favorite=user.id)

        return queryset

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def add_recipe_to_fav_or_cart(self, recipe, serializer, request):
        if request.method == 'POST':
            recipe.add(request.user)
            return Response(serializer.data, status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            recipe.remove(request.user),
            return Response(status.HTTP_204_NO_CONTENT)

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk=None):
        """ Add recipe to favorites """
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteRecipeSerializer(recipe)
        return self.add_recipe_to_fav_or_cart(
            recipe.favorite, serializer, request)

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """ Add recipe to shopping cart """
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteRecipeSerializer(recipe)
        return self.add_recipe_to_fav_or_cart(recipe.cart, serializer, request)

    @action(methods=('get',),
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request):
        """ Downloads a PDF list of all ingredients for recipes in cart """
        ingredients = CustomUser.objects.filter(id=request.user.id).values(
            'shopping_cart__ingredients__name',
            'shopping_cart__ingredients__measurement_unit',
        ).exclude(shopping_cart__ingredients__name__isnull=True).annotate(
            total=Sum('shopping_cart__ingredients__ingredient_amount'),
        ).order_by('shopping_cart__ingredients__name')

        # Adding font supporting cyrillic alphabet
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        # Generating PDF file with reportlab
        buf = io.BytesIO()
        page = canvas.Canvas(buf, pagesize=A4, bottomup=0)
        text_obj = page.beginText()
        text_obj.setTextOrigin(inch, inch)
        text_obj.setFont('DejaVuSans', 14)
        text_obj.setLeading(leading=25)
        text_obj.textLine(f'Список покупок {request.user.username}:')
        ingredient_num = 0
        for i in ingredients:
            ingredient_num += 1
            text_obj.textLine(
                f'{ingredient_num}. ' + ' '.join(str(i) for i in i.values()))

        page.drawText(text_obj)
        page.showPage()
        page.save()
        buf.seek(0)

        return FileResponse(buf, as_attachment=True,
                            filename='Foodgram_cart.pdf')


class TagViewSet(ReadOnlyModelViewSet):
    """
    Tags can only be added and edited via admin panel.
    """
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Ingredients can only be added and edited via admin panel.
    """
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
