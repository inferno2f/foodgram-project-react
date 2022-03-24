import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api.models import Ingredient, Recipe, Tag
from api.paginators import DefaultPaginator
from api.permissions import IsAuthorOrReadOnly, IsUserOrReadOnly
from api.serializers import (ChangePasswordSerializer, CreateUserSerializer,
                             FavoriteRecipeSerializer, GetUserSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer, UserSubscribtionSerializer)
from users.models import CustomUser, Follow


class UserViewSet(ModelViewSet):
    """Viewset for all user-related opertations. Uses djoser endpoints"""
    queryset = CustomUser.objects.all()
    permission_classes = (IsUserOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return GetUserSerializer

    @action(methods=('get',),
            detail=False, permission_classes=(IsUserOrReadOnly,))
    def me(self, request):
        """ Quick access to user's peronal profile via /me endpoint """
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = CreateUserSerializer(user, many=False)
        return Response(serializer.data)

    @action(methods=('post',),
            detail=False, permission_classes=(IsUserOrReadOnly,))
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

    @action(methods=('get', 'delete'),
            detail=True, permission_classes=(IsUserOrReadOnly,))
    def subscribe(self, request, pk):
        author = get_object_or_404(CustomUser, id=pk)
        user = request.user
        serializer = UserSubscribtionSerializer(data=request.data)
        follow = Follow.objects.filter(user=user, author=author)

        # FIXME: разобраться с сериализаторами
        if request.method == 'GET':
            serializer = UserSubscribtionSerializer(follow)
            if not follow:
                serializer = UserSubscribtionSerializer(
                    Follow.objects.create(user=user, author=author))
                serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if follow:
                Follow.objects.filter(user=user, author=author).delete()
                return Response(
                    {'detail': 'success'},
                    status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'subscription doesn\'t exist'},
                status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('tag',)
    ordering = ('-id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @ action(methods=('get', 'delete'), detail=True,
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

    @ action(methods=('get', 'delete'), detail=True,
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

    @ action(methods=('get',),
            permission_classes=(permissions.IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request):
        """ Download list of all ingredients for recipes in shopping cart """
        ingredients = CustomUser.objects.filter(id=request.user.id).values(
            'shopping_cart__ingredients__name',
            'shopping_cart__ingredients__units',
        ).exclude(shopping_cart__ingredients__name__isnull=True).annotate(
            total=Sum('shopping_cart__recipeingredients__amount'),
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
        paginator = DefaultPaginator()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = IngredientSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.filter(id=pk)
        # ingredient = get_object_or_404(queryset, pk=pk)
        serializer = IngredientSerializer(queryset)
        return Response(serializer.data)
