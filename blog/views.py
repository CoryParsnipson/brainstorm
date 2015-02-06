from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError, ValidationError
from django.core.context_processors import csrf
from django.http import JsonResponse
from django.views.generic import View
from django.utils.http import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, response

import lib
from models import Idea, Thought
from forms import LoginForm, IdeaForm, ThoughtForm
from serializers import UserSerializer, IdeaSerializer, ThoughtSerializer


###############################################################################
# Site skeleton views
###############################################################################
def index(request):
    latest_thoughts = Thought.objects.filter(is_draft=False, is_trash=False).order_by("-date_published")[:9]

    small_stories = latest_thoughts[1:]
    for t in small_stories:
        t.content = t.truncate()

    # prepare html output for big story
    if len(latest_thoughts):
        latest_thought = latest_thoughts[0]
        latest_thought.content = latest_thought.truncate()
    else:
        latest_thought = None

    context = {
        'page_title': 'Home',
        'latest_thought': latest_thought,
        'latest_thoughts': small_stories,
    }
    return render(request, 'blog/index.html', context)


def login_page(request):
    if request.user.is_authenticated():
        # redirect straight to dashboard
        return redirect('dashboard')

    context = {
        'page_title': 'Login',
        'login_form': LoginForm()
    }
    return render(request, 'blog/login.html', context)


def logout_page(request):
    context = {'page_title': 'Logout'}
    return render(request, 'blog/logout.html', context)


def about(request):
    context = {'page_title': 'About'}
    return render(request, 'blog/about.html', context)


def ideas(request):
    idea_list = Idea.objects.all()

    for idea in idea_list:
        idea.description = idea.truncate()

    context = {'page_title': 'Ideas',
               'ideas': idea_list}
    return render(request, 'blog/ideas.html', context)


def idea_detail(request, idea_slug=None):
    idea = get_object_or_404(Idea, slug=idea_slug)
    thoughts = Thought.objects.filter(idea=idea_slug, is_draft=False, is_trash=False).order_by('-date_published')

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
    context = {
        'page_title': 'Main',
    }
    return render(request, 'blog/dashboard/dashboard.html', context)


@login_required(login_url='index')
def dashboard_ideas(request):
    """ User dashboard page to edit/create/manage Idea objects.

        ?i=[idea slug]  specify a slug in query string to edit an idea
    """
    # obtain all the Ideas
    idea_list = Idea.objects.all().order_by("order")

    # form for editing/creating a new idea
    idea_form_instance = None
    if 'i' in request.GET:
        try:
            # sanitize query parameter
            idea_slug = lib.slugify(request.GET['i'])
            idea_form_instance = Idea.objects.get(slug=idea_slug)
        except Idea.DoesNotExist as e:
            dne_msg = "Cannot edit Idea '%s'" % idea_slug
            messages.add_message(request, messages.ERROR, dne_msg)
    new_idea_form = IdeaForm(instance=idea_form_instance)

    context = {
        'page_title': 'Manage Ideas',
        'new_idea_form': new_idea_form,
        'ideas': idea_list,
    }
    return render(request, 'blog/dashboard/dashboard_ideas.html', context)


@login_required(login_url='index')
def dashboard_thoughts(request):
    # thought data
    thoughts = []
    current_idea = None

    if 'idea_slug' in request.GET:
        try:
            current_idea = Idea.objects.get(slug=request.GET['idea_slug'])
            thoughts = Thought.objects.filter(idea=current_idea, is_draft=False, is_trash=False)
        except Idea.DoesNotExist:
            thoughts = []

    context = {
        'page_title': 'Manage Thoughts',
        'thoughts': thoughts,
        'idea': current_idea
    }
    return render(request, 'blog/dashboard/dashboard_thoughts.html', context)


@login_required(login_url='index')
def dashboard_author(request):
    """ User dashboard page to write new thoughts, edit old ones, or work on drafts.

        ?thought_slug=[thought slug] provide a slug to edit a thought or draft
    """
    # create thought form (or load instance data if editing a thought)
    thought_form_instance = None
    if 'thought_slug' in request.GET:
        try:
            thought_slug = lib.slugify(request.GET['thought_slug'])
            thought_form_instance = Thought.objects.get(slug=thought_slug)
        except Thought.DoesNotExist as e:
            pass
    new_thought_form = ThoughtForm(instance=thought_form_instance)

    context = {
        'page_title': 'Write New Thought',
        'new_thought_form': new_thought_form,
    }
    return render(request, 'blog/dashboard/dashboard_author.html', context)


@login_required(login_url='index')
def dashboard_drafts(request):
    """ User dashboard page to manage drafts
    """
    thoughts = Thought.objects.filter(is_draft=True, is_trash=False).order_by('-idea')
    tags = ['a', 'strong', 'em']

    drafts = {}
    for t in thoughts:
        t.content = t.truncate(max_length=100, allowed_tags=tags)

        if t.idea not in drafts:
            drafts[t.idea] = []
        drafts[t.idea].append(t)

    context = {
        'page_title': 'Drafts',
        'drafts': drafts,
    }
    return render(request, 'blog/dashboard/dashboard_drafts.html', context)


@login_required(login_url='index')
def dashboard_trash(request):
    """ user dashboard page to manage thoughts in trash
    """
    thoughts = Thought.objects.filter(is_trash=True).order_by("date_published")
    tags = ['a', 'strong', 'em']

    trash = {}
    for t in thoughts:
        t.content = t.truncate(max_length=100, allowed_tags=tags)

        if t.idea not in trash:
            trash[t.idea] = []
        trash[t.idea].append(t)

    context = {
        'page_title': 'Trash',
        'thoughts': trash,
    }
    return render(request, 'blog/dashboard/dashboard_trash.html', context)


@login_required(login_url='index')
def dashboard_backend(request):
    query_string = ""
    if 'next' in request.POST:
        next_url = request.POST['next']
    else:
        next_url = reverse('dashboard-thoughts')

    if 'trash' in request.POST or 'untrash' in request.POST:
        trash = True if 'trash' in request.POST else False
        result = thought_set_trash(request.POST['thought_slug'], trash=trash)

        if result:
            try:
                thought_slug = lib.slugify(request.POST['thought_slug'])
                thought = Thought.objects.get(slug=thought_slug)

                if trash:
                    be_msg = "Thought %s was trashed. " % thought.slug
                    be_msg += "<form action='%s' method='post'>" % reverse('dashboard-backend')
                    be_msg += "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % unicode(csrf(request)['csrf_token'])
                    be_msg += "<input type='hidden' name='thought_slug' value='%s' />" % thought.slug

                    if 'next' in request.POST:
                        be_msg += '<input type="hidden" name="next" value="%s" />' % request.POST['next']

                    be_msg += "<input type='submit' name='untrash' value='Undo' />"
                    be_msg += "</form>"
                    messages.add_message(request, messages.SUCCESS, be_msg)

                query_string = urlencode({
                    'idea_slug': thought.idea.slug,
                })
            except Thought.DoesNotExist as e:
                pass
    elif 'unpublish' in request.POST:
        thought_unpublish(request.POST['thought_slug'])
        thought = Thought.objects.get(slug=request.POST['thought_slug'])
        query_string = urlencode({
            'idea_slug': thought.idea.slug,
        })
    elif 'delete_thought' in request.POST:
        thought_delete(request.POST['thought_slug'])
    elif 'delete_idea' in request.POST:
        try:
            safe_delete_idea(request.POST['idea'])
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, e.message)
    elif 'order_up' in request.POST or 'order_down' in request.POST:
        try:
            err_msg = None
            idea_slug = lib.slugify(request.POST['idea'])
            idea = Idea.objects.get(slug=idea_slug)

            if 'order_up' in request.POST:
                adjacent_idea = idea.get_next()
            else:
                adjacent_idea = idea.get_prev()

            if adjacent_idea:
                swap_ideas(idea_slug, adjacent_idea.slug)
        except KeyError as e:
            err_msg = e.message
        except Idea.DoesNotExist as e:
            err_msg = e.message
        finally:
            if err_msg:
                messages.add_message(request, messages.ERROR, err_msg)

    return redirect(next_url + "?" + query_string)


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
        return redirect(reverse('logout-page'))


@login_required(login_url='index')
def logout(request):
    auth_logout(request)
    messages.add_message(request, messages.INFO, 'Successfully logged out.')
    return redirect(reverse('logout-page'))


@login_required(login_url='index')
def upload(request):
    """ server logic for handling file/image/video/mp3 uploads
    """
    files = {}

    if request.method == 'POST':
        for file_input, f in request.FILES.items():
            result, files[f.name] = lib.upload_file(f)

        return JsonResponse(files)
    return JsonResponse({'msg': 'Unsupported method for Upload. (POST only)'})


###############################################################################
# helper functions
###############################################################################
def get_adjacent_thought(thought_slug, get_next=True, num=1, include_drafts=False, include_trash=False):
    """ get the next or previous Thought in the same Idea and return the
        thought object
    """
    try:
        thought = Thought.objects.get(slug=thought_slug)
    except ValueError as e:
        print e.message
        return []

    query_params = {
        'idea': thought.idea,
        'is_draft': False,
        'is_trash': False,
    }

    if include_drafts:
        del query_params['is_draft']

    if include_trash:
        del query_params['is_trash']

    thought_list = Thought.objects.filter(**query_params)

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


def swap_ideas(idea_slug, adjacent_idea_slug):
    """ swap an idea with another given idea (based on the order column)

        returns True on success, False on error
    """
    idea_slug = lib.slugify(idea_slug)
    adjacent_idea_slug = lib.slugify(adjacent_idea_slug)

    try:
        idea = Idea.objects.get(slug=idea_slug)
        adjacent_idea = Idea.objects.get(slug=adjacent_idea_slug)

        # swap the ordering on these two ideas
        order = adjacent_idea.order

        # order is unique, obliterate one value and save
        adjacent_idea.order = -1
        adjacent_idea.save()

        adjacent_idea.order = idea.order
        idea.order = order

        idea.save()
        adjacent_idea.save()
    except Idea.DoesNotExist:
        return False
    return True


def thought_set_trash(thought_slug, trash=True):
    """ set the is_trash field on a given Thought.

        return True on success, False on failure
    """
    try:
        thought_slug = lib.slugify(thought_slug)
        thought = Thought.objects.get(slug=thought_slug)

        thought.is_trash = trash
        thought.save()
    except Thought.DoesNotExist as e:
        return False
    return True


def thought_unpublish(thought_slug):
    """ Select a thought by the slug and change the is_draft field
        back to True
    """
    thought_slug = lib.slugify(thought_slug)

    try:
        thought = Thought.objects.get(slug=thought_slug)
        thought.is_draft = True
        thought.save()
    except Thought.DoesNotExist:
        return False
    return True


def thought_delete(thought_slug):
    """ Delete a thought specified by thought_slug
    """
    thought_slug = lib.slugify(thought_slug)

    try:
        thought = Thought.objects.get(slug=thought_slug)
        thought.delete()
    except Thought.DoesNotExist:
        return False
    return True


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

            ?draft=["true"|"false"|"both"] specify to include drafts, false by default\n
            ?trash=["true"|"false"|"both"] specify to include trashed thoughts, false by default\n

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

        # exclude drafts by default
        query_string_params['is_draft'] = False
        if 'draft' in request.GET:
            if request.GET['draft'] == "both":
                del query_string_params['is_draft']
            elif request.GET['draft'] == "true":
                query_string_params['is_draft'] = True

        query_string_params['is_trash'] = False
        if 'trash' in request.GET:
            if request.GET['trash'] == "both":
                del query_string_params['is_trash']
            elif request.GET['trash'] == "true":
                # trash should show drafts too
                query_string_params['is_trash'] = True
                del query_string_params['is_draft']

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

        # TODO: make draft thought require admin permissions to pull

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
        msgs = {}

        url_pass = None
        if 'url_pass' in instance_data:
            url_pass = instance_data['url_pass']
            del instance_data['url_pass']

        query_string = ""
        if 'q' in instance_data:
            query_string = "?" + instance_data['q']

        if 'qdict' in instance_data:
            query_string = "?" + urlencode(instance_data['qdict'])

        if 'slug' not in instance_data or not instance_data['slug']:
            instance_data['slug'] = lib.slugify(instance_data['name'])
        else:
            instance_data['slug'] = lib.slugify(instance_data['slug'])

        try:
            instance = Idea.objects.get(slug=instance_data['slug'])
            msgs['msg'] = "Successfully edited Idea %s" % instance.slug
        except Idea.DoesNotExist as e:
            instance = None
            msgs['msg'] = "Successfully created Idea %s" % instance_data['slug']
        idea_form = IdeaForm(instance_data, request.FILES, instance=instance)

        if idea_form.is_valid():
            idea_form.save()
            if url_pass:
                return redirect(reverse(url_pass) + query_string)
            else:
                return JsonResponse(msgs)
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

            request.POST['next'] optional url for redirect on completion
            request.POST['q'] optional query string parameters (urlencoded)
            request.POST['qdict'] optional query string in dictionary form
        """
        instance_data = request.POST.copy()
        msgs = {}

        callback = None
        if 'next' in instance_data:
            callback = instance_data['next']
            del instance_data['next']

        if 'is_draft' in instance_data:
            instance_data['is_draft'] = True
        else:
            instance_data['is_draft'] = False

        query_string = ""
        if 'q' in instance_data:
            query_string = "?" + instance_data['q']

        if 'qdict' in instance_data:
            query_string = "?" + urlencode(instance_data['qdict'])

        if 'slug' not in instance_data or not instance_data['slug']:
            instance_data['slug'] = lib.slugify(instance_data['title'])
        else:
            instance_data['slug'] = lib.slugify(instance_data['slug'])

        try:
            instance = Thought.objects.get(slug=instance_data['slug'])
            msgs['msg'] = "Successfully edited Thought %s" % instance.slug
        except Thought.DoesNotExist as e:
            instance = None
            msgs['msg'] = "Successfully created Thought %s" % instance_data['slug']
        thought_form = ThoughtForm(instance_data, request.FILES, instance=instance)

        if thought_form.is_valid():
            thought_form.save()
            idea = Idea.objects.filter(slug=instance_data['idea'])[0]

            if callback:
                if callback == 'default':
                    kwargs = {
                        'thought_slug': instance_data['slug'],
                        'idea_slug': instance_data['idea'],
                    }
                    callback = reverse('thought-detail', kwargs=kwargs)
                return redirect(callback + query_string)
            else:
                return JsonResponse(msgs)
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            for field in thought_form:
                errors[field.name] = field.errors

            if callback:
                err_msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, err_msg)
                return redirect(reverse('dashboard-author') + query_string)
            else:
                return JsonResponse(errors)