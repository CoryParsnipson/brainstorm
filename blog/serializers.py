from django.contrib.auth.models import User, Group

from rest_framework import serializers

from blog.models import Idea, Thought

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')


class IdeaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Idea
        fields = ('name', 'description')


class ThoughtSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Thought
        fields = ('title', 'content', 'author', 'date_published', 'date_edited', 'idea')
