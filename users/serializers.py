from rest_framework import serializers, validators
from django.contrib.auth.models import User

from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    # notes = serializers.StringRelatedField(many=True)
    email = serializers.EmailField(
                validators=[
                    validators.UniqueValidator(queryset=User.objects.all())
                ]
            )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


# class ProfileSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(many=False)
#     class Meta:
#         model = Profile
#         fields = ('profile_pic',)
