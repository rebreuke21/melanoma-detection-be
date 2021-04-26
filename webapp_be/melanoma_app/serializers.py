from django.contrib.auth.models import Group
from .models import User, Image, Image_Classification
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ImageSerializer(serializers.ModelSerializer):
    image_classification = serializers.CharField(source="image_classification.classification")
    image = serializers.ImageField()
    region = serializers.CharField(source="region.region")
    lesion_id = serializers.IntegerField()
    description = serializers.CharField()

    class Meta:
        model = Image
        fields = (  "image",
                    "image_classification",
                    "region",
                    "lesion_id",
                    "description")
    
    """def get_image_location(self, image):
        request = self.context.get('request')
        image_location = image
        return request.build_absolute_uri(image_location)"""
