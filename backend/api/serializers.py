from django.contrib.auth import password_validation
from rest_framework import serializers, validators

from api.fields import Base64ImageField
from api.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import CustomUser, Follow


class CreateUserSerializer(serializers.ModelSerializer):
    """ Serializer for CustomUser model.
    Reuqired fields:
        ['username', 'email', 'password', 'first_name', 'last_name']
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
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


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
    """ Serializer for a 'GET' method of a CustomUserViewSet """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

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


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers. ReadOnlyField(source='ingredient.id')
    name = serializers. ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """ Serializer for RecipeIngredient model """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """ Serializer for reading Recipe model """
    author = GetUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return GetRecipeIngredientSerializer(ingredients, many=True).data

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


class CreateOrUpdateRecipeSerialzer(serializers.ModelSerializer):
    """ Serializer for creating a new recipe """
    ingredients = AddRecipeIngredientSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def _add_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

    def _check_for_duplicate_tags(self, data):
        """ Checks if the same tag is added twice """
        for item in data['tags']:
            if data['tags'].count(item) > 1:
                raise serializers.ValidationError(
                    'You cannot add the same tag twice')

    def _check_for_duplicate_ingredients(self, data):
        """ Checks if the same ingredient is added twice """
        ingredients = []
        for item in data['ingredients']:
            if item['id'] in ingredients:
                raise serializers.ValidationError(
                    'You cannot add the same ingredient twice')
            ingredients.append(item['id'])

    def validate(self, data):
        self._check_for_duplicate_ingredients(data)
        self._check_for_duplicate_tags(data)
        return data

    def to_representation(self, instance):
        serializer = GetRecipeSerializer(
            instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        self._add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class ShortUserSerilazier(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')


class FollowSerializer(serializers.ModelSerializer):
    """ Serializer for subscriptions page """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = FavoriteRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return FavoriteRecipeSerializer(recipes, many=True,
                                        context=context).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author']
            )
        ]
