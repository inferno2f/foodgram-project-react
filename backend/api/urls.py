from email.mime import base
from django.urls import include, path
from rest_framework import routers

from api import views


router = routers.SimpleRouter()
router.register('users', views.UserViewSet)
router.register('tag', views.TagViewSet, basename='Tag')
router.register('recipe', views.RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
