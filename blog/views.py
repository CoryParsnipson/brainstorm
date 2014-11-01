from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import viewsets

from blog.models import Idea
from blog.serializers import UserSerializer, IdeaSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class IdeaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing Ideas
    """
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer