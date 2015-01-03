import urllib

from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError, ValidationError
from django.http import JsonResponse
from django.views.generic import View
from django.utils.http import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, response

from models import Idea, Thought, slugify
from forms import LoginForm, IdeaForm, ThoughtForm
from serializers import UserSerializer, IdeaSerializer, ThoughtSerializer

import common

###############################################################################
# Site skeleton views
###############################################################################
def index(request):
    latest_thoughts = Thought.objects.all().order_by("-date_published")[:9]
    context = {'page_title': 'Home',
               'latest_thought': latest_thoughts[0] if len(latest_thoughts) else None,
               'latest_thoughts': latest_thoughts[1:]}
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


def ideas(request):
    idea_list = Idea.objects.all()
    context = {'page_title': 'Ideas',
               'ideas': idea_list}
    return render(request, 'blog/ideas.html', context)


def about(request):
    context = {'page_title': 'About'}
    return render(request, 'blog/about.html', context)


def idea_detail(request, idea_slug=None):
    idea = get_object_or_404(Idea, slug=idea_slug)
    thoughts = Thought.objects.filter(idea=idea_slug).order_by('-date_published')

    context = {
        'page_title': idea.name,
        'idea': idea,
        'thoughts': thoughts
        }
    return render(request, 'blog/idea.html', context)


def thought_detail(request, idea_slug=None, thought_slug=None):
    thought = get_object_or_404(Thought, slug=thought_slug)

    next_thoughts = get_adjacent_thought(thought_slug=thought.slug, get_next=True, num=3)
    prev_thoughts = get_adjacent_thought(thought_slug=thought.slug, get_next=False, num=3)

    context = {
        'page_title': thought.title,
        'thought': thought,
        'next_thoughts': next_thoughts,
        'prev_thoughts': prev_thoughts
    }
    return render(request, 'blog/thought.html', context)


###############################################################################
# site admin sections
###############################################################################
@login_required(login_url='index')
def dashboard(request, *args, **kwargs):
    idea_page = 1
    ideas_per_page = common.Globals.ideas_per_page

    if 'per_page' in request.GET:
        try:
            if request.GET['per_page'] > 0 and request.GET['per_page'] <= common.Globals.ideas_per_page:
                ideas_per_page = request.GET['per_page']
        except TypeError as e:
            ideas_per_page = common.Globals.ideas_per_page

    num_ideas = Idea.objects.all().count()
    num_pages = (num_ideas / ideas_per_page) + (1 if num_ideas % ideas_per_page else 0)

    if 'page' in request.GET and request.GET['page'] > 0 and request.GET['page'] >= num_pages:
        try:
            idea_page = int(request.GET['page'])
        except TypeError as e:
            idea_page = 1

    # paginate ideas
    idea_page_start = (idea_page - 1) * ideas_per_page
    idea_page_end = idea_page_start + ideas_per_page
    idea_list = Idea.objects.all()[idea_page_start:idea_page_end]

    # create idea form (or load instance data if editing an idea)
    idea_form_instance = None
    if 'edit_idea' in request.GET:
        try:
            idea_form_instance = Idea.objects.get(slug=request.GET['edit_idea'])
        except Idea.DoesNotExist as e:
            pass
    idea_form = IdeaForm(instance=idea_form_instance)

    # create thought form (or load instance data if editing a thought)
    thought_form_instance = None
    if 'edit_thought' in request.GET:
        try:
            thought_form_instance = Thought.objects.get(slug=request.GET['edit_thought'])
        except Thought.DoesNotExist as e:
            pass
    thought_form = ThoughtForm(instance=thought_form_instance)

    # thought data
    thoughts = []
    if 'idea_slug' in request.GET and request.GET['idea_slug']:
        current_idea = Idea.objects.get(slug=request.GET['idea_slug'])
        if current_idea:
            thoughts = Thought.objects.filter(idea=current_idea)

    context = {'page_title': 'Main',
               'ideas': idea_list,
               'idea_form': idea_form,
               'thoughts': thoughts,
               'thought_form': thought_form,
               'idea_pages': range(1, num_pages + 1)}
    return render(request, 'blog/dashboard/dashboard.html', context)


@login_required(login_url='index')
def dashboard_manage_idea(request):
    messages.add_message(request, messages.INFO, "OMG I love cocks.")

    if 'edit' in request.POST:
        return redirect(reverse('dashboard') + "?edit_idea=" + request.POST['idea'])

    if 'delete' in request.POST:
        try:
            safe_delete_idea(request.POST['idea'])
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, e.message)
        return redirect(reverse('dashboard'))


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
# helper functions
###############################################################################
def get_adjacent_thought(thought_slug, get_next=True, num=1):
    """ get the next or previous Thought in the same Idea and return the
        thought object
    """
    try:
        thought = Thought.objects.get(slug=thought_slug)
    except ValueError as e:
        print e.message
        return []

    thought_list = Thought.objects.filter(idea=thought.idea)

    current_thought_idx = -1
    for idx, item in enumerate(thought_list):
        if thought == item:
            current_thought_idx = idx

    try:
        if get_next:
            start_idx = current_thought_idx + 1
            adjacent_thoughts = thought_list[start_idx:start_idx + num]
        else:
            start_idx = max(current_thought_idx - num, 0)
            adjacent_thoughts = thought_list[start_idx:current_thought_idx]
    except (AssertionError, IndexError) as e:
        return []

    return adjacent_thoughts


def safe_delete_idea(idea_slug):
    """ delete a given idea (identified by idea_slug) only if it has no
        associated thoughts. Else do not delete and raise ValidationError
    """

    idea = Idea.objects.get(slug=idea_slug)
    thoughts = Thought.objects.filter(idea=idea)

    if len(thoughts) > 0:
        raise ValidationError("Cannot delete Idea %s; has associated thoughts" % idea.name)
    idea.delete()


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

    def destroy(self, request, *args, **kwargs):
        """ delete an idea. This function has been overridden from the default
            behavior to only delete an idea if there are no thoughts associated
            with it. Otherwise it raises an error.

            kwargs['slug'] id to identify idea
            kwargs['redirect'] url to redirect; if blank, send empty Response
        """
        safe_delete_idea(kwargs['slug'])

        if 'redirect' in kwargs:
            return redirect(kwargs['redirect'])
        return response.Response()


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

        if 'order' in request.GET:
            try:
                thoughts = thoughts.order_by(request.GET['order'])
            except FieldError as e:
                pass

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

        data = [ThoughtSerializer(t).data for t in thoughts]
        return response.Response(data=data)

    def retrieve(self, request, *args, **kwargs):
        """ retrieve a specific Thought object identified by primary key
            (slug field). You can also do things like get the previous/next
            Thought in the Idea.\n\n

            ?next=[int] if this is set, get the next Thought (or empty str)\n
                        the integer value determines how many Thoughts to return \n\n

            ?prev=[int] if this is set, get the previous Thought (or empty str)\n
                        the integer value determines how many Thoughts to return \n\n
        """
        try:
            thought = Thought.objects.get(slug=kwargs['slug'])
        except ValueError as e:
            return response.Response()

        if 'next' in request.GET or 'prev' in request.GET:
            get_next = 'next' in request.GET
            thought_range = 1

            try:
                if 'next' in request.GET:
                    thought_range = int(request.GET['next'])
                elif 'prev' in request.GET:
                    thought_range = int(request.GET['prev'])
            except ValueError:
                thought_range = 1

            adjacent_thoughts = get_adjacent_thought(thought_slug=thought.slug, get_next=get_next, num=thought_range)

            if adjacent_thoughts:
                data = [ThoughtSerializer(t).data for t in adjacent_thoughts]
                return response.Response(data=data)
            else:
                return response.Response()

        data = ThoughtSerializer(thought).data
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
            request.POST['q'] optional query string parameters (urlencoded)
            request.POST['qdict'] optional query string in dictionary form
        """
        instance_data = request.POST.copy()

        url_pass = 'dashboard'
        if 'url_pass' in instance_data:
            url_pass = instance_data['url_pass']
            del instance_data['url_pass']

        query_string = ""
        if 'q' in instance_data:
            query_string = "?" + instance_data['q']

        if 'qdict' in instance_data:
            query_string = "?" + urlencode(instance_data['qdict'])

        if 'slug' in instance_data and not instance_data['slug']:
            instance_data['slug'] = slugify(instance_data['name'])

        try:
            instance = Idea.objects.get(slug=instance_data['slug'])
        except Idea.DoesNotExist as e:
            instance = None
        idea_form = IdeaForm(instance_data, instance=instance)

        if idea_form.is_valid():
            idea_form.save()
            return redirect(reverse(url_pass) + query_string)
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
            request.POST['q'] optional query string parameters (urlencoded)
            request.POST['qdict'] optional query string in dictionary form
        """
        instance_data = request.POST.copy()

        url_pass = 'dashboard'
        if 'url_pass' in instance_data:
            url_pass = instance_data['url_pass']
            del instance_data['url_pass']

        query_string = ""
        if 'q' in instance_data:
            query_string = "?" + instance_data['q']

        if 'qdict' in instance_data:
            query_string = "?" + urlencode(instance_data['qdict'])

        if 'slug' in instance_data and not instance_data['slug']:
            instance_data['slug'] = slugify(instance_data['title'])

        try:
            instance = Thought.objects.get(slug=instance_data['slug'])
        except Thought.DoesNotExist as e:
            instance = None
        thought_form = ThoughtForm(instance_data, instance=instance)

        if thought_form.is_valid():
            thought_form.save()
            idea = Idea.objects.filter(slug=instance_data['idea'])[0]
            return redirect(reverse(url_pass) + query_string)
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            i = 0
            for field in thought_form:
                errors[field.name] = field.errors
                i += 1

            return JsonResponse(errors)