from django_filters import rest_framework

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
