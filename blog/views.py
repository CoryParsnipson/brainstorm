from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from rest_framework import viewsets, response
from rest_framework.decorators import detail_route

from blog.models import Idea, Thought
from blog.forms import IdeaForm, ThoughtForm
from blog.serializers import UserSerializer, IdeaSerializer, ThoughtSerializer


###############################################################################
# Site skeleton views
###############################################################################
def index(request):
    context = {'page_title': 'Home'}
    return render(request, 'blog/index.html', context)

def dashboard(request):
    context = {'page_title': 'Dashboard'}
    return render(request, 'blog/dashboard.html', context)

def idea_detail(request, idea_slug):
    # TODO: raise exception on bad ID
    idea = Idea.objects.filter(slug=idea_slug)

    context = {'page_title': idea[0].name,
               'idea_slug': idea_slug,
               'idea_id': idea[0].id}
    return render(request, 'blog/idea.html', context)


###############################################################################
# RESTful API
###############################################################################
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
    lookup_field = 'slug'

    @detail_route()
    def thoughts(self, request, slug):
        idea = Idea.objects.filter(slug=slug)
        thoughts = Thought.objects.filter(idea=idea)
        return response.Response(data=[ThoughtSerializer(t).data for t in thoughts])


class ThoughtViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing Thoughts
    """
    queryset = Thought.objects.all()
    serializer_class = ThoughtSerializer
    lookup_field = 'slug'


# form handling views
class FormIdeaView(View):
    """ API endpoints for forms to manage user interaction for Ideas
    """
    def get(self, request, *args, **kwargs):
        """ return form body output for a form to create a new idea
        """
        idea_form = IdeaForm()
        idea_form_output = idea_form.as_table()

        if "output" in request.GET:
            if request.GET["output"] == "p":
                idea_form_output = idea_form.as_p()
            elif request.GET["output"] == "ul":
                idea_form_output = idea_form.as_ul()

        context = {'form': idea_form_output}
        return JsonResponse(context)

    # TODO: set form action to "", use ajax to call post and receive json response
    def post(self, request, *args, **kwargs):
        """ save the POST data for the form into a new Idea
        """
        idea_form = IdeaForm(request.POST)
        new_idea = idea_form.save()
        return redirect(reverse('idea_detail', args=(new_idea.id,)), permanent=True)


class FormThoughtView(View):
    """ API endpoints for forms to manage user interactions and Thoughts
    """
    def get(self, request, *args, **kwargs):
        """ return form body output for a form to create a new thought
        """
        form = ThoughtForm()
        form_html = form.as_table()

        if "output" in request.GET:
            if request.GET["output"] == "p":
                form_html = form.as_p()
            elif request.GET["output"] == "ul":
                form_html = form.as_ul()

        context = {'form': form_html}
        return JsonResponse(context)

    # TODO: set form action to "", use ajax to call post and receive json response
    def post(self, request, *args, **kwargs):
        """ save the POST data to create a new Thought
        """
        thought_form = ThoughtForm(request.POST)

        if thought_form.is_valid():
            thought_form.save()

            idea = Idea.objects.filter(id=request.POST['idea'])[0]
            return redirect(reverse('idea_detail', args=(idea.slug,)))
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            i = 0
            for field in thought_form:
                errors[field.name] = field.errors
                i += 1

            return JsonResponse(errors)