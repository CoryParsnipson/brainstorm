from django.contrib.auth.models import User, Group

from rest_framework import serializers

from blog.models import Idea, Thought


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class IdeaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Idea
        fields = ('id', 'name', 'description')


class ThoughtSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.PrimaryKeyRelatedField(many=False)
    idea = serializers.PrimaryKeyRelatedField(many=False)

    class Meta:
        model = Thought
        fields = ('title', 'content', 'author', 'date_published', 'date_edited', 'idea')
