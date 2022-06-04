from django_filters import rest_framework
from rest_framework.filters import BaseFilterBackend

from api.models import Ingredient


class IngredientFilter(rest_framework.FilterSet):
    """ Lookup filter for Ingredient model. """
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(BaseFilterBackend):
    """ Lookup filter for Recipe model. """
    def filter_queryset(self, request, queryset, view):

        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = request.query_params.get('is_in_shopping_cart')
        if is_in_shopping == '1':
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping == '0':
            queryset = queryset.exclude(cart=user.id)

        is_favorited = request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorite=user.id)
        if is_favorited == '0':
            queryset = queryset.exclude(favorite=user.id)

        return queryset
