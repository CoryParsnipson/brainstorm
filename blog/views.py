from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework import response

from blog.models import Idea, Thought
from blog.serializers import UserSerializer, IdeaSerializer, ThoughtSerializer


# Create your views here.
class MainSiteView:
    """
    'Normal' views organized into a little class, just for tidy-ness. Contains
    views for top level "news headlines" portion of the site.
    """
    @staticmethod
    def index(request):
        context = {'page_title': 'Home'}
        return render(request, 'blog/index.html', context)

    @staticmethod
    def dashboard(request):
        context = {'page_title': 'Dashboard'}
        return render(request, 'blog/dashboard.html', context)

    @staticmethod
    def idea(request):
        # TODO: raise exception on bad ID
        idea_id = request.GET.get('id', None)
        idea = Idea.objects.filter(id=idea_id)

        context = {'page_title': idea[0].name}
        return render(request, 'blog/idea.html', context)


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

