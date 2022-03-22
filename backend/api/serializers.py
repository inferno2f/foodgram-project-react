from django.contrib.auth import password_validation
from rest_framework import serializers

from api.models import Tag, Recipe
from users.models import CustomUser, Follow


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    Reuqired fields: ['username', 'email', 'password', 'first_name', 'last_name']
    """
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=150, required=True)

    def validate_email(self, value):
        """Checks if the email is already in the database"""
        lower_email = value.lower()
        if CustomUser.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError(
                'This email address is already in use')
        return lower_email

    def validate_username(self, value):
        """ Assures that username is not taken or equal to 'me' """
        lower_username = value.lower()
        if lower_username == 'me' or CustomUser.objects.filter(
                username=lower_username).exists():
            raise serializers.ValidationError(
                'Please use a different username')
        return lower_username

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class GetUserSerializer(serializers.ModelSerializer):
    """ Serializer for a 'GET' method of a UserViewSet """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(id=obj.id).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    tag = serializers.StringRelatedField(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            # 'image',
            'description',
            'ingredients',
            'tag',
            'time',
            'is_favorite',
        )

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(id=obj.id).exists()
        return False

class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """ Shortened serializer to view favorite recipes """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'time')
