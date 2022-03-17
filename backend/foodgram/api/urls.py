from email.mime import base
from django.urls import include, path
from rest_framework import routers

from api import views


router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'tag', views.TagViewSet, basename='Tag')

urlpatterns = [
    path('', include(router.urls)),
]
