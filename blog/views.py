from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import viewsets

from blog.models import Idea, Thought
from blog.serializers import UserSerializer, IdeaSerializer, ThoughtSerializer


# Create your views here.
class MainSiteView:
    """
    'Normal' views organized into a little class, just for tidyness. Contains
    views for top level "news headlines" portion of the site.
    """
    @staticmethod
    def index(request):
        context = {}
        return render(request, 'blog/index.html', context)


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

class ThoughtViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing Thoughts
    """
    queryset = Thought.objects.all()
    serializer_class = ThoughtSerializer

