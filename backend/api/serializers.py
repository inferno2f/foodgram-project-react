from django.contrib.auth import password_validation
from django.db.models import F
from rest_framework import serializers

from api.models import Tag, Recipe, Ingredient, RecipeIngredients
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
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


# class RecipeIngredientsSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField(source='ingredient.id')
#     name = serializers.ReadOnlyField(source='ingredient.name')
#     measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
#     amount = serializers.ReadOnlyField(source='recipeingredient.amount')

#     class Meta:
#         model = RecipeIngredients
#         fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class RecipeSerializer(serializers.ModelSerializer):
    author = GetUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'description',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
    
    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient_amount__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(id=obj.id).exists()
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """ Shortened serializer to view favorite recipes """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# FIXME: Этот сериализатор не работает, полностью переделать recipes и распарсить данные автора!
class UserSubscribtionSerializer(serializers.ModelSerializer):
    # recipes = FavoriteRecipeSerializer(many=True, read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'author',
            # 'user__email',
            # 'following__id',
            # 'following__username',
            # 'following__first_name',
            # 'following__last_name',
            # 'author__is_subscribed',
            'recipes'
         )
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = Recipe.objects.filter(author=obj.author)
        return FavoriteRecipeSerializer(queryset, many=True).data
