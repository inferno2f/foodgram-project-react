from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from .serializers import CreateUserSerializer
from users.models import User


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)
