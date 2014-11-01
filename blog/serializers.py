from django.contrib.auth.models import User, Group

from rest_framework import serializers

from blog.models import Idea

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')


class IdeaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Idea
        fields = ('name', 'description')


#class ThoughtSerializer(serializers.Serializer):
