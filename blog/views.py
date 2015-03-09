import random

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.context_processors import csrf
from django.http import JsonResponse
from django.views.generic import View
from django.utils.http import urlencode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

import lib
from models import Idea, Thought, Highlight
from forms import LoginForm, IdeaForm, ThoughtForm, HighlightForm


###############################################################################
# Site skeleton views
###############################################################################
def index(request):
    thoughts = Thought.objects.filter(is_draft=False, is_trash=False).order_by("-date_published")

    latest_thought = None
    if len(thoughts):
        latest_thought = thoughts[0]
        latest_thought.content = latest_thought.truncate(max_length=240)

    thoughts = thoughts[1:]

    page = request.GET.get('p')
    paginator, thoughts_on_page = lib.create_paginator(
        queryset=thoughts,
        per_page=lib.PAGINATION_FRONT_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=thoughts,
        current_page=page,
        per_page=lib.PAGINATION_FRONT_PER_PAGE,
        page_lead=lib.PAGINATION_FRONT_PAGES_TO_LEAD,
    )

    for t in thoughts_on_page:
        t.content = t.truncate()

    # get latest link of the day
    highlight = Highlight.objects.all().order_by('-date_published')[:1]
    highlight_cut = False
    if highlight:
        highlight = highlight[0]
        highlight.description = highlight.truncate(max_length=90)
        highlight_cut = len(highlight.description) > 90

    context = {
        'page_title': 'Home',
        'latest_thought': latest_thought,
        'latest_thoughts': thoughts_on_page,
        'paginator': paginator,
        'pagination': pagination,
        'highlight': highlight,
        'highlight_cut': highlight_cut,
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
    context = {
        'page_title': 'Logout'
    }
    return render(request, 'blog/logout.html', context)


def highlights(request):
    highlight_list = Highlight.objects.all().order_by('-date_published')

    page = request.GET.get('p')
    paginator, highlights_on_page = lib.create_paginator(
        queryset=highlight_list,
        per_page=lib.PAGINATION_HIGHLIGHTS_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=highlight_list,
        current_page=page,
        per_page=lib.PAGINATION_HIGHLIGHTS_PER_PAGE,
        page_lead=lib.PAGINATION_HIGHLIGHTS_PAGES_TO_LEAD,
    )

    context = {
        'page_title': 'Highlights',
        'highlights': highlights_on_page,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/highlights.html', context)


def about(request):
    context = {
        'page_title': 'About'
    }
    return render(request, 'blog/about.html', context)


def ideas(request):
    idea_list = Idea.objects.all().order_by('order')

    page = request.GET.get('p')
    paginator, ideas_on_page = lib.create_paginator(
        queryset=idea_list,
        per_page=lib.PAGINATION_IDEAS_PER_PAGE,
        page=page,
    )

    pagination_main = lib.create_pagination(
        queryset=idea_list,
        current_page=page,
        per_page=lib.PAGINATION_IDEAS_PER_PAGE,
        page_lead=lib.PAGINATION_IDEAS_PAGES_TO_LEAD,
    )

    for idea in idea_list:
        idea.description = idea.truncate()

    # create more recent ideas list
    thoughts = Thought.objects.filter(is_draft=False, is_trash=False)
    recent_ideas = [t['idea'] for t in thoughts.order_by('-date_published').values('idea')]
    recent_ideas = lib.remove_duplicates(recent_ideas)[:lib.NUM_RECENT_IDEAS]

    recent_thoughts = []
    for idea_slug in recent_ideas:
        recent_thoughts += Thought.objects.filter(idea=idea_slug).order_by('-date_published')[:1]

    for t in recent_thoughts:
        t.content = t.truncate(max_length=100)

    context = {
        'page_title': 'Ideas',
        'ideas': ideas_on_page,
        'paginator': paginator,
        'pagination': pagination_main,
        'recent_thoughts': recent_thoughts,
    }
    return render(request, 'blog/ideas.html', context)


def idea_detail(request, idea_slug=None):
    idea = get_object_or_404(Idea, slug=idea_slug)
    thoughts = Thought.objects.filter(idea=idea_slug, is_draft=False, is_trash=False).order_by('-date_published')

    page = request.GET.get('p')
    paginator, thoughts_on_page = lib.create_paginator(
        queryset=thoughts,
        per_page=lib.PAGINATION_THOUGHTS_PER_PAGE,
        page=page,
    )

    pagination_main = lib.create_pagination(thoughts, page)
    pagination_side = lib.create_pagination(
        queryset=thoughts,
        current_page=page,
        per_page=lib.PAGINATION_THOUGHTS_PER_PAGE,
        page_lead=0,
    )

    for t in thoughts_on_page:
        t.content = t.truncate()

    # pick from a list, prevent duplicates
    other_ideas = Idea.objects.exclude(slug=idea_slug)
    indices = range(0, len(other_ideas))
    footer_ideas = []
    while indices and len(footer_ideas) < lib.NUM_IDEAS_FOOTER:
        idx = random.randint(1, len(indices)) - 1
        footer_ideas.append(other_ideas[indices[idx]])
        del indices[idx]

    context = {
        'page_title': idea.name,
        'idea': idea,
        'footer_ideas': footer_ideas,
        'thoughts': thoughts_on_page,
        'paginator': paginator,
        'pagination': pagination_main,
        'pagination_side': pagination_side,
    }
    return render(request, 'blog/idea.html', context)


def thought_detail(request, idea_slug=None, thought_slug=None):
    thought = get_object_or_404(Thought, slug=thought_slug)

    # make sure trashed thoughts and drafts can only be viewed by
    # an authenticated, admin user
    if thought.is_draft or thought.is_trash:
        if not request.user.is_authenticated() or not request.user.is_superuser:
            msg = "Unauthorized to view Thought..."
            messages.add_message(request, messages.WARNING, msg)
            return redirect(reverse('index'))

    context = {
        'page_title': thought.title,
        'thought': thought,
        'next_thoughts': thought.get_next_thoughts(num=1),
        'prev_thoughts': thought.get_prev_thoughts(num=3),
    }
    return render(request, 'blog/thought.html', context)


###############################################################################
# site admin sections
###############################################################################
@login_required(login_url='index')
def dashboard(request, *args, **kwargs):
    # collect dashboard stats
    stats = dashboard_stats()

    context = {
        'page_title': 'Main',
        'stats': stats,
    }
    return render(request, 'blog/dashboard/dashboard.html', context)


@login_required(login_url='index')
def dashboard_highlights(request):
    """ User dashboard page to manage Link of the Day
    """
    highlight_list = Highlight.objects.all().order_by('-date_published')

    paginator, highlights_on_page = lib.create_paginator(
        queryset=highlight_list,
        per_page=lib.PAGINATION_HIGHLIGHTS_PER_PAGE,
        page=request.GET.get('p'),
    )

    pagination = lib.create_pagination(
        queryset=highlight_list,
        current_page=request.GET.get('p'),
        per_page=lib.PAGINATION_HIGHLIGHTS_PER_PAGE,
        page_lead=lib.PAGINATION_HIGHLIGHTS_PAGES_TO_LEAD,
    )

    for h in highlights_on_page:
        h.description = h.truncate(max_length=75, allowed_tags=['a'])

    instance = None
    if 'highlight' in request.GET:
        try:
            instance = Highlight.objects.get(id=request.GET['highlight'])
        except Highlight.DoesNotExist:
            pass
    highlight_form = HighlightForm(instance=instance)

    context = {
        'page_title': 'Highlights',
        'highlights': highlights_on_page,
        'highlight_form': highlight_form,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/dashboard/dashboard_highlights.html', context)


@login_required(login_url='index')
def dashboard_ideas(request):
    """ User dashboard page to edit/create/manage Idea objects.

        ?i=[idea slug]  specify a slug in query string to edit an idea
    """
    # obtain all the Ideas
    idea_list = Idea.objects.all().order_by("order")

    page = request.GET.get('p')
    paginator, ideas_on_page = lib.create_paginator(
        queryset=idea_list,
        per_page=lib.PAGINATION_DASHBOARD_IDEAS_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=idea_list,
        current_page=page,
        per_page=lib.PAGINATION_DASHBOARD_IDEAS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_IDEAS_PAGES_TO_LEAD,
    )

    for i in ideas_on_page:
        i.description = i.truncate(max_length=50)

    # form for editing/creating a new idea
    idea_form_instance = None
    if 'i' in request.GET:
        try:
            # sanitize query parameter
            idea_slug = lib.slugify(request.GET['i'])
            idea_form_instance = Idea.objects.get(slug=idea_slug)
        except Idea.DoesNotExist:
            dne_msg = "Cannot edit Idea '%s'" % idea_slug
            messages.add_message(request, messages.ERROR, dne_msg)
    idea_form = IdeaForm(instance=idea_form_instance)

    context = {
        'page_title': 'Manage Ideas',
        'idea_form': idea_form,
        'ideas': ideas_on_page,
        'paginator': paginator,
        'pagination': pagination,
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
    else:
        thoughts = Thought.objects.filter(is_draft=False, is_trash=False)

    page = request.GET.get('p')
    paginator, thoughts_on_page = lib.create_paginator(
        queryset=thoughts,
        per_page=lib.PAGINATION_DASHBOARD_THOUGHTS_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=thoughts,
        current_page=page,
        per_page=lib.PAGINATION_DASHBOARD_THOUGHTS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_THOUGHTS_PAGES_TO_LEAD,
    )

    # collect dashboard stats
    stats = dashboard_stats()

    context = {
        'page_title': 'Manage Thoughts',
        'thoughts': thoughts_on_page,
        'idea': current_idea,
        'stats': stats,
        'paginator': paginator,
        'pagination': pagination,
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
    thought_form = ThoughtForm(instance=thought_form_instance)

    context = {
        'page_title': 'Write New Thought',
        'thought_form': thought_form,
    }
    return render(request, 'blog/dashboard/dashboard_author.html', context)


@login_required(login_url='index')
def dashboard_drafts(request):
    """ User dashboard page to manage drafts
    """
    drafts = Thought.objects.filter(is_draft=True, is_trash=False).order_by('-date_published')

    page = request.GET.get('p')
    paginator, drafts_on_page = lib.create_paginator(
        queryset=drafts,
        per_page=lib.PAGINATION_DASHBOARD_DRAFTS_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=drafts,
        current_page=page,
        per_page=lib.PAGINATION_DASHBOARD_DRAFTS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_DRAFTS_PAGES_TO_LEAD,
    )

    tags = ['a', 'strong', 'em']
    for t in drafts_on_page:
        t.content = t.truncate(max_length=50, allowed_tags=tags)

    context = {
        'page_title': 'Drafts',
        'drafts': drafts_on_page,
        'paginator': paginator,
        'pagination': pagination,
        'stats': dashboard_stats(),
    }
    return render(request, 'blog/dashboard/dashboard_drafts.html', context)


@login_required(login_url='index')
def dashboard_trash(request):
    """ user dashboard page to manage thoughts in trash
    """
    trash = Thought.objects.filter(is_trash=True).order_by("date_published")

    page = request.GET.get('p')
    paginator, trash_on_page = lib.create_paginator(
        queryset=trash,
        per_page=lib.PAGINATION_DASHBOARD_DRAFTS_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=trash,
        current_page=page,
        per_page=lib.PAGINATION_DASHBOARD_DRAFTS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_DRAFTS_PAGES_TO_LEAD,
    )

    tags = ['a', 'strong', 'em']
    for t in trash_on_page:
        t.content = t.truncate(max_length=100, allowed_tags=tags)

    context = {
        'page_title': 'Trash',
        'trash': trash_on_page,
        'paginator': paginator,
        'pagination': pagination,
        'stats': dashboard_stats(),
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
                    be_msg = "<form action='%s' method='post' class='group'>" % reverse('dashboard-backend')
                    be_msg += "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % unicode(csrf(request)['csrf_token'])
                    be_msg += "<input type='hidden' name='thought_slug' value='%s' />" % thought.slug

                    if 'next' in request.POST:
                        be_msg += '<input type="hidden" name="next" value="%s" />' % request.POST['next']

                    be_msg += "<p>Thought %s was trashed.</p>" % thought.slug
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

        msg = "Moved Thought '%s' to Drafts." % thought.slug
        messages.add_message(request, messages.SUCCESS, msg)
    elif 'delete_thought' in request.POST:
        if thought_delete(request.POST['thought_slug']):
            msg = "Successfully deleted Thought '%s'" % request.POST['thought_slug']
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            msg = "Error: Thought '%s' does not exist." % request.POST['thought_slug']
            messages.add_message(request, messages.ERROR, msg)
    elif 'delete_idea' in request.POST:
        try:
            safe_delete_idea(request.POST['idea'])
            msg = "Successfully deleted Idea '%s'" % request.POST['idea']
            messages.add_message(request, messages.SUCCESS, msg)
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, e.message)
    elif 'order_up' in request.POST or 'order_down' in request.POST:
        err_msg = None
        try:
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
    elif 'delete_highlight' in request.POST:
        try:
            highlight = Highlight.objects.get(id=request.POST['highlight'])
            highlight_title = highlight.title
            highlight.delete()

            msg = "Successfully deleted Link '%s'" % highlight_title
            messages.add_message(request, messages.SUCCESS, msg)
        except Highlight.DoesNotExist:
            pass

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


def dashboard_stats():
    """ compile statistics from database and return a dictionary object.

        Stat keys:

    """
    stats = {
        'thought_count': Thought.objects.filter(is_draft=False, is_trash=False).count(),
        'draft_count': Thought.objects.filter(is_draft=True, is_trash=False).count(),
        'trash_count': Thought.objects.filter(is_trash=True).count(),
        'idea_count': Idea.objects.all().count(),
        'highlight_count': Highlight.objects.all().count(),
    }
    return stats


###############################################################################
# Form handling views
###############################################################################
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

            request.POST['next'] optional url for redirect on completion
        """
        instance_data = request.POST.copy()
        msgs = {}

        callback = None
        if 'next' in instance_data:
            callback = instance_data['next']
            del instance_data['next']
            lib.replace_tokens(callback, instance_data)

        if 'slug' not in instance_data or not instance_data['slug']:
            instance_data['slug'] = lib.slugify(instance_data['name'])
        else:
            instance_data['slug'] = lib.slugify(instance_data['slug'])

        try:
            instance = Idea.objects.get(slug=instance_data['slug'])
            msgs['msg'] = "Successfully edited Idea %s" % instance.name
        except Idea.DoesNotExist as e:
            instance = None
            msgs['msg'] = "Successfully created Idea %s" % instance_data['name']
        idea_form = IdeaForm(instance_data, request.FILES, instance=instance)

        if idea_form.is_valid():
            idea_form.save()
            if callback:
                messages.add_message(request, messages.SUCCESS, msgs['msg'])
                return redirect(callback)
            return JsonResponse(msgs)
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            i = 0
            for field in idea_form:
                errors[field.name] = field.errors
                i += 1

            if callback:
                msg = errors
                messages.add_message(request, messages.ERROR, msg)
                return redirect(callback)
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
            request.POST['old_slug'] may be None, used to edit value of slug
        """
        instance_data = request.POST.copy()
        msgs = {}

        callback = None
        if 'next' in instance_data:
            callback = instance_data['next']
            del instance_data['next']
            callback = lib.replace_tokens(callback, {'idea': instance_data['idea']})

        if 'is_draft' in instance_data:
            instance_data['is_draft'] = True
        else:
            instance_data['is_draft'] = False

        if 'slug' not in instance_data or not instance_data['slug']:
            instance_data['slug'] = lib.slugify(instance_data['title'])
        else:
            instance_data['slug'] = lib.slugify(instance_data['slug'])

        old_slug = lib.slugify(instance_data['old_slug'])
        del instance_data['old_slug']

        # compare against old slug to check if we have edited the slug or if there is a collision
        if not old_slug:
            new_slug = instance_data['slug']
            slug_collision_index = 2

            while Thought.objects.filter(slug=new_slug).exists():
                new_slug = instance_data['slug'] + "-" + str(slug_collision_index)
                slug_collision_index += 1

            instance_data['slug'] = new_slug
        else:
            # disallow editing of slugs
            instance_data['slug'] = old_slug

        try:
            instance = Thought.objects.get(slug=instance_data['slug'])
            msgs['msg'] = "Successfully edited Thought '%s'" % instance.slug
        except Thought.DoesNotExist as e:
            instance = None
            if instance_data['is_draft']:
                msgs['msg'] = "Saved draft '%s' for later." % instance_data['slug']
            else:
                msgs['msg'] = "Successfully created Thought '%s'" % instance_data['slug']
        thought_form = ThoughtForm(instance_data, request.FILES, instance=instance)

        if thought_form.is_valid():
            thought_form.save()
            idea = Idea.objects.filter(slug=instance_data['idea'])[0]

            if instance_data['is_draft']:
                messages.add_message(request, messages.WARNING, msgs['msg'])
            else:
                messages.add_message(request, messages.SUCCESS, msgs['msg'])

            if callback:
                if callback == 'default':
                    kwargs = {
                        'thought_slug': instance_data['slug'],
                        'idea_slug': instance_data['idea'],
                    }
                    callback = reverse('thought-page', kwargs=kwargs)
                return redirect(callback)
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
                return redirect(reverse('dashboard-author'))
            else:
                return JsonResponse(errors)


class FormHighlightView(View):
    """ API endpoints for forms to manage user interactions and Links
    """
    def get(self, request, *args, **kwargs):
        """ return form body output for a form to create a new link
        """
        form = HighlightForm()
        form_html = form.as_table()

        if "output" in request.GET:
            if request.GET["output"] == "p":
                form_html = form.as_p()
            elif request.GET["output"] == "ul":
                form_html = form.as_ul()

        context = {'form': form_html}
        return JsonResponse(context)

    def post(self, request, *args, **kwargs):
        """ Save POST data to create a new Link of the Day

            request.POST['next'] optional url for redirect on completion
        """
        instance_data = request.POST.copy()

        callback = None
        if 'next' in instance_data:
            callback = instance_data['next']
            del instance_data['next']
            lib.replace_tokens(callback, instance_data)

        if 'cancel' in instance_data:
            return redirect(callback)

        if 'id' not in instance_data or not instance_data['id']:
            instance_data['id'] = -1

        try:
            instance = Highlight.objects.get(id=instance_data['id'])
            msg = "Successfully edited Link '%s'" % instance.title
        except Highlight.DoesNotExist as e:
            instance = None
            msg = "Successfully created Link '%s'" % instance_data['title'] if 'title' in instance_data else None

        link_form = HighlightForm(instance_data, request.FILES, instance=instance)

        if link_form.is_valid():
            link_form.save()
            messages.add_message(request, messages.SUCCESS, msg)

            if callback:
                return redirect(callback)
            else:
                return JsonResponse({'msg': msg})
        else:
            # loop through fields on form and add errors to dict
            errors = {}
            for field in link_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(callback)
            else:
                return JsonResponse(errors)