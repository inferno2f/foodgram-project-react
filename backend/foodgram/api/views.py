from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api.models import Tag
from api.serializers import CreateUserSerializer, TagSerializer
from users.models import CustomUser


class UserViewSet(ModelViewSet):
    """Viewset for all user-related opertations. Uses djoser endpoints"""
    queryset = CustomUser.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (permissions.AllowAny,)

class TagViewSet(ViewSet):
    def list(self, request):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)
