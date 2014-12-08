from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, response

from models import Idea, Thought
from forms import LoginForm, IdeaForm, ThoughtForm
from serializers import UserSerializer, IdeaSerializer, ThoughtSerializer


###############################################################################
# Site skeleton views
###############################################################################
def index(request):
    context = {'page_title': 'Home',
               'login_form': LoginForm()}
    return render(request, 'blog/index.html', context)


def login_page(request):
    if request.user.is_authenticated():
        # redirect straight to dashboard
        return redirect('dashboard')

    context = {'page_title': 'Login',
               'login_form': LoginForm()}
    return render(request, 'blog/login.html', context)


def logout_page(request):
    context = {'page_title': 'Logout'}
    return render(request, 'blog/logout.html', context)


@login_required(login_url='index')
def dashboard(request):
    ideas = Idea.objects.all()
    idea_form = IdeaForm()
    thought_form = ThoughtForm()
    context = {'page_title': 'Dashboard',
               'ideas': ideas,
               'idea_form': idea_form,
               'thought_form': thought_form,
               'user': request.user}
    return render(request, 'blog/dashboard.html', context)


def ideas(request):
    idea_list = Idea.objects.all()
    context = {'page_title': 'Ideas',
               'ideas': idea_list}
    return render(request, 'blog/ideas.html', context)


def about(request):
    context = {'page_title' : 'About'}
    return render(request, 'blog/about.html', context)


def idea_detail(request, idea_slug=None):
    # TODO: raise exception on bad ID
    idea = Idea.objects.filter(slug=idea_slug)

    context = {'page_title': idea[0].name,
               'idea_slug': idea_slug}
    return render(request, 'blog/idea.html', context)


###############################################################################
# Miscellaneous API
###############################################################################
def login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return redirect(dashboard)
    else:
        messages.add_message(request, messages.ERROR, 'Invalid login credentials provided.')
        return redirect(logout_page)


@login_required(login_url='index')
def logout(request):
    auth_logout(request)
    messages.add_message(request, messages.INFO, 'Successfully logged out.')
    return redirect(logout_page)


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


class ThoughtViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing Thoughts
    """
    queryset = Thought.objects.all()
    serializer_class = ThoughtSerializer
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        """ return a JSON object container containing Thought objects.
        Supply optional query string parameters to modify the returned set.\n\n

        ?idea=[slug] or [int] to select all Thoughts of an Idea\n
        ?author=[int] id of User; select all Thoughts authored by User\n
        ?older_than=[str] all Thoughts older than 'yyyy-mm-dd hh:mm'\n
        ?newer_than=[str] all Thoughts newer than 'yyyy-mm-dd hh:mm'\n
        ?exclude="true" if set, negates filter parameters\n

        ?count=[int] total number of Thoughts to return\n
        ?slice=[int]:[int] works like python list slice\n

        ?order=[string] name of field, prepend "-" to reverse order, e.g. "+date" (requires exact name of SQL field)\n
        """
        query_string_params = {}

        if 'idea' in request.GET:
            query_string_params['idea'] = request.GET['idea']

        if 'author' in request.GET:
            query_string_params['author'] = int(request.GET['author'])

        if 'older_than' in request.GET:
            query_string_params['date_published__lt'] = request.GET['older_than']

        if 'newer_than' in request.GET:
            query_string_params['date_published__gt'] = request.GET['newer_than']

        # do database query and "post processing"
        if 'exclude' in request.GET and request.GET['exclude'] == "true":
            thoughts = Thought.objects.exclude(**query_string_params)
        else:
            thoughts = Thought.objects.filter(**query_string_params)

        if 'count' in request.GET:
            thoughts = thoughts[:request.GET['count']]

        if 'slice' in request.GET:
            start_idx, end_idx = request.GET['slice'].split(":")
            try:
                start_idx = int(start_idx) if start_idx else None
                end_idx = int(end_idx) if end_idx else None

                thoughts = thoughts[start_idx:end_idx]
            except ValueError as e:
                pass

        if 'order' in request.GET:
            try:
                thoughts = thoughts.order_by(request.GET['order'])
            except FieldError as e:
                pass

        data = [ThoughtSerializer(t).data for t in thoughts]
        return response.Response(data=data)


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

    def post(self, request, *args, **kwargs):
        """ save the POST data for the form into a new Idea

            request.POST['url_pass'] optional url for redirect on completion
        """
        url_pass = 'dashboard'
        if 'url_pass' in request.POST:
            url_pass = request.POST['url_pass']
            del request.POST['url_pass']

        idea_form = IdeaForm(request.POST)

        if idea_form.is_valid():
            idea_form.save()
            return redirect(reverse(url_pass))
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            i = 0
            for field in idea_form:
                errors[field.name] = field.errors
                i += 1

            return JsonResponse(errors)


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

    def post(self, request, *args, **kwargs):
        """ save the POST data to create a new Thought

            request.POST['url_pass'] optional url for redirect on completion
        """
        url_pass = 'dashboard'
        if 'url_pass' in request.POST:
            url_pass = request.POST['url_pass']
            del request.POST['url_pass']

        thought_form = ThoughtForm(request.POST)

        if thought_form.is_valid():
            thought_form.save()
            idea = Idea.objects.filter(slug=request.POST['idea'])[0]
            return redirect(reverse(url_pass, args=(idea.slug,)))
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            i = 0
            for field in thought_form:
                errors[field.name] = field.errors
                i += 1

            return JsonResponse(errors)