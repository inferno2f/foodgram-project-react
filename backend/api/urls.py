from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.SimpleRouter()
router.register('users', views.CustomUserViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet, basename='Tag')
router.register('ingredients', views.IngredientViewSet, basename='Ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
