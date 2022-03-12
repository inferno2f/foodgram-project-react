from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet


router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(r'api/auth/', include('djoser.urls')),
    path(r'api/auth/token/login', include('djoser.urls.authtoken')),
]
