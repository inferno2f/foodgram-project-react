from rest_framework import serializers

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=32, required=True)
    last_name = serializers.CharField(max_length=32, required=True)
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Checks if the email is already in the database"""
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
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
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        return user

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
