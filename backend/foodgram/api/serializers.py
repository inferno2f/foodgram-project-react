from rest_framework import serializers

from users.models import CustomUser
from api.models import Tag


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    Reuqired fields: ['username', 'email', 'password', 'first_name', 'last_name']
    """
    first_name = serializers.CharField(max_length=32, required=True)
    last_name = serializers.CharField(max_length=32, required=True)
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Checks if the email is already in the database"""
        lower_email = value.lower()
        if CustomUser.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError(
                'This email address is already in use')
        return lower_email

    def validate_username(self, value):
        """ Assures that username is not equal to 'me' """
        lower_username = value.lower()
        if lower_username == 'me':
            raise serializers.ValidationError(
                'Please use a different username')
        return lower_username

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
