import os
import urllib
import random

from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.context_processors import csrf
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import View
from django.utils.http import urlquote_plus
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

import lib
import paths
from models import Idea, Thought, Highlight, ReadingListItem, Task, Activity
from forms import LoginForm, IdeaForm, ThoughtForm, HighlightForm, ReadingListItemForm, TaskForm


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
        highlight.description = highlight.truncate(
            max_length=90,
            full_link=reverse('highlights'))
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
        'login_form': LoginForm(),
    }
    return render(request, 'blog/login.html', context)


def logout_page(request):
    context = {
        'page_title': 'Logout',
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


def books(request):
    read_book_list_total = ReadingListItem.objects.filter(wishlist=False).order_by('-date_published')

    page = request.GET.get('p')
    paginator, read_list = lib.create_paginator(
        queryset=read_book_list_total,
        per_page=lib.PAGINATION_READINGLIST_PER_PAGE,
        page=page,
    )
    pagination = lib.create_pagination(
        queryset=read_book_list_total,
        current_page=page,
        per_page=lib.PAGINATION_READINGLIST_PER_PAGE,
        page_lead=lib.PAGINATION_READINGLIST_PAGES_TO_LEAD,
    )

    context = {
        'page_title': 'Reading List',
        'wish_list': ReadingListItem.objects.filter(wishlist=True).order_by('-date_published'),
        'read_list': read_list,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/books.html', context)


def about(request):
    context = {
        'page_title': 'About',
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
    recent_thoughts = Thought.objects.filter(is_draft=False, is_trash=False).order_by('-date_published')

    recent_ideas = [t['idea'] for t in recent_thoughts.values('idea')]
    unique_ideas = lib.remove_duplicates([t['idea'] for t in recent_thoughts.values('idea')])[:lib.NUM_RECENT_IDEAS]

    recent_thoughts = [recent_thoughts[recent_ideas.index(i)] for i in unique_ideas]

    allowed_tags = list(Thought.allowed_tags) + ['img']
    for t in recent_thoughts:
        t.content = t.truncate(allowed_tags=allowed_tags)

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
        t.content = t.truncate(
            max_length=175,
            full_link=reverse('thought-page', kwargs={
                'idea_slug': t.idea.slug,
                'thought_slug': t.slug,
            }),
        )

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
    }
    return render(request, 'blog/thought.html', context)


###############################################################################
# site admin sections
###############################################################################
@login_required(login_url='index')
def dashboard(request):
    activities = Activity.objects.all().order_by("-date")
    paginator, activities_on_page = lib.create_paginator(
        queryset=activities,
        per_page=lib.PAGINATION_DASHBOARD_ACTIVITY_PER_PAGE,
        page=request.GET.get('p'),
    )

    pagination = lib.create_pagination(
        queryset=activities,
        current_page=request.GET.get('p'),
        per_page=lib.PAGINATION_DASHBOARD_ACTIVITY_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_ACTIVITY_PAGES_TO_LEAD,
    )

    context = {
        'page_title': 'Main',
        'activities': activities_on_page,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/dashboard/dashboard.html', context)


@login_required(login_url='index')
def dashboard_books(request):
    """ User dashboard page to manage reading list

        ?id=[book id]   specify a book id to edit a book
    """
    instance = None
    if 'id' in request.GET:
        try:
            instance = ReadingListItem.objects.get(id=request.GET['id'])
        except ReadingListItem.DoesNotExist:
            pass
    reading_list_item_form = ReadingListItemForm(instance=instance)

    read_list_total = ReadingListItem.objects.filter(wishlist=False).order_by('-date_published')
    paginator, read_list = lib.create_paginator(
        queryset=read_list_total,
        per_page=lib.PAGINATION_DASHBOARD_READINGLIST_PER_PAGE,
        page=request.GET.get('p'),
    )

    pagination = lib.create_pagination(
        queryset=read_list_total,
        current_page=request.GET.get('p'),
        per_page=lib.PAGINATION_DASHBOARD_READINGLIST_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_READINGLIST_PAGES_TO_LEAD,
    )

    context = {
        'page_title': 'Books',
        'wish_list': ReadingListItem.objects.filter(wishlist=True).order_by('-date_published'),
        'read_list': read_list,
        'reading_list_item_form': reading_list_item_form,
        'paginator': paginator,
        'pagination': pagination
    }
    return render(request, 'blog/dashboard/dashboard_books.html', context)


@login_required(login_url='index')
def dashboard_highlights(request):
    """ User dashboard page to manage Highlights on the Web

        ?id=[highlight id]   specify an id to edit an idea
    """
    highlight_list = Highlight.objects.all().order_by('-date_published')

    paginator, highlights_on_page = lib.create_paginator(
        queryset=highlight_list,
        per_page=lib.PAGINATION_DASHBOARD_HIGHLIGHTS_PER_PAGE,
        page=request.GET.get('p'),
    )

    pagination = lib.create_pagination(
        queryset=highlight_list,
        current_page=request.GET.get('p'),
        per_page=lib.PAGINATION_DASHBOARD_HIGHLIGHTS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_HIGHLIGHTS_PAGES_TO_LEAD,
    )

    for h in highlights_on_page:
        h.description = h.truncate(max_length=75, allowed_tags=['a'])

    instance = None
    if 'id' in request.GET:
        try:
            instance = Highlight.objects.get(id=request.GET['id'])
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
def dashboard_todo(request):
    """ user dashboard page to manage Task object instances
    """
    if 'c' in request.GET:
        tasks = Task.objects.filter(parent_task__isnull=True)
    else:
        tasks = Task.objects.filter(is_completed=False, parent_task__isnull=True)

    tasks = Task.reorder_child_tasks(tasks, 'c' in request.GET)

    page = request.GET.get('p')
    paginator, tasks_on_page = lib.create_paginator(
        queryset=tasks,
        per_page=lib.PAGINATION_DASHBOARD_TASKS_PER_PAGE,
        page=page,
    )

    pagination = lib.create_pagination(
        queryset=tasks,
        current_page=page,
        per_page=lib.PAGINATION_DASHBOARD_TASKS_PER_PAGE,
        page_lead=lib.PAGINATION_DASHBOARD_TASKS_PAGES_TO_LEAD,
    )

    context = {
        'page_title': 'Tasks',
        'tasks': tasks_on_page,
        'paginator': paginator,
        'pagination': pagination,
        'task_form': TaskForm(),
    }
    return render(request, 'blog/dashboard/dashboard_todo.html', context)


@login_required(login_url='index')
def dashboard_ideas(request):
    """ User dashboard page to edit/create/manage Idea objects.

        ?id=[idea slug]  specify a slug in query string to edit an idea
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
    idea_slug = None
    idea_form_instance = None
    if 'id' in request.GET:
        try:
            # sanitize query parameter
            idea_slug = lib.slugify(request.GET['id'])
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
    try:
        idea = None
        filter_params = {
            'is_draft': False,
            'is_trash': False,
        }

        if 'id' in request.GET:
            idea = Idea.objects.get(slug=lib.slugify(request.GET['id']))
            filter_params['idea'] = idea

        thoughts = Thought.objects.filter(**filter_params).order_by("-date_published")
    except Idea.DoesNotExist:
        return redirect(reverse('dashboard-ideas'))

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

    context = {
        'page_title': 'Manage Thoughts',
        'thoughts': thoughts_on_page,
        'idea': idea,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/dashboard/dashboard_thoughts.html', context)


@login_required(login_url='index')
def dashboard_author(request):
    """ User dashboard page to write new thoughts, edit old ones, or work on drafts.

        ?id=[thought slug] provide a slug to edit a thought or draft
    """
    # create thought form (or load instance data if editing a thought)
    thought_form_instance = None
    if 'id' in request.GET:
        try:
            thought_slug = lib.slugify(request.GET['id'])
            thought_form_instance = Thought.objects.get(slug=thought_slug)
        except Thought.DoesNotExist:
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

    context = {
        'page_title': 'Drafts',
        'drafts': drafts_on_page,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/dashboard/dashboard_drafts.html', context)


@login_required(login_url='index')
def dashboard_trash(request):
    """ user dashboard page to manage thoughts in trash
    """
    trash = Thought.objects.filter(is_trash=True).order_by("-date_published")

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

    context = {
        'page_title': 'Trash',
        'trash': trash_on_page,
        'paginator': paginator,
        'pagination': pagination,
    }
    return render(request, 'blog/dashboard/dashboard_trash.html', context)


@login_required(login_url='index')
def dashboard_backend(request):
    if 'next' in request.POST:
        next_url = request.POST['next']
    else:
        next_url = request.META['HTTP_REFERER']

    # gather checked ids
    if not 'id' in request.POST:
        messages.add_message(request, messages.WARNING, "No items selected for action!")
        return redirect(next_url)

    action = request.POST['action'] if 'action' in request.POST else ''
    action_args = action.split('|')
    action = action_args[0]
    action_args = action_args[1:]

    fmm = lib.FlashMessageManager()
    for i in request.POST.getlist('id'):
        if action == 'idea_delete':
            idea_name = Idea.objects.filter(slug=i)[0].name
            status, tokens = idea_safe_delete(i)
            if status:
                # log activity in database
                a = Activity()
                a.author = request.user
                a.type = Activity.get_type_id('Deleted Idea')
                a.store_tokens({'name': idea_name, 'slug': i})
                a.url = reverse('dashboard-ideas')
                a.save()

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': ''})
        elif action == 'idea_order_up' or action == 'idea_order_down':
            try:
                idea_slug = lib.slugify(i)
                idea = Idea.objects.get(slug=idea_slug)

                if action == 'idea_order_up':
                    adjacent_idea = idea.get_next()
                else:
                    adjacent_idea = idea.get_prev()

                if adjacent_idea:
                    idea_swap_order(idea.slug, adjacent_idea.slug)
            except Exception as e:
                fmm.add_message({'action': action, 'status': False, 'tokens': {'error': e.message}, 'extra_html': ''})
        elif action == 'thought_trash' or action == 'thought_untrash':
            status, tokens = thought_trash(i, action == 'thought_trash')
            t = Thought.objects.filter(slug=i)[0]

            if action == 'thought_trash':
                if status:
                    # log activity in database
                    a = Activity()
                    a.author = request.user
                    a.type = Activity.get_type_id('Trashed Draft' if t.is_draft else 'Trashed Thought')
                    a.store_tokens({'length': 1, 'title': t.title, 'slug': t.slug})
                    a.url = reverse('dashboard-trash')
                    a.save()

                undo = undo_button_html(request, input_data={'action': 'thought_untrash'})
            else:
                if status:
                    # log activity in database
                    a = Activity()
                    a.author = request.user
                    a.type = Activity.get_type_id('Untrashed Draft' if t.is_draft else 'Untrashed Thought')
                    a.store_tokens({'length': 1, 'title': t.title, 'slug': t.slug})
                    a.url = reverse('dashboard-author') + "?id=" + t.slug
                    a.save()

                undo = undo_button_html(request, input_data={'action': 'thought_trash'})

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': undo})
        elif action == 'thought_unpublish' or action == 'thought_publish':
            t = Thought.objects.filter(slug=i)[0]
            t_is_draft = t.is_draft
            auto_update = request.POST['auto_update'] if 'auto_update' in request.POST else False
            status, tokens = thought_publish(i, action == 'thought_publish', auto_update)

            if action == 'thought_unpublish':
                if status:
                    # log activity in database
                    a = Activity()
                    a.author = request.user
                    a.type = Activity.get_type_id('Unpublished Thought')
                    a.store_tokens({'length': 1, 'title': t.title, 'slug': t.slug})
                    a.url = reverse('dashboard-author') + "?id=" + t.slug
                    a.save()

                undo = undo_button_html(request, input_data={'action': 'thought_publish'})
            else:
                if status and t_is_draft:
                    # log activity in database
                    a = Activity()
                    a.author = request.user
                    a.type = Activity.get_type_id('Published Draft')
                    a.store_tokens({'length': 1, 'title': t.title, 'slug': t.slug})
                    a.url = reverse('dashboard-author') + "?id=" + t.slug
                    a.save()

                undo = undo_button_html(request, input_data={'action': 'thought_unpublish'})

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': undo})
        elif action == 'thought_idea_move':
            t = Thought.objects.filter(slug=i)[0]
            t_old_idea = t.idea.name
            status, tokens = thought_move(i, action_args[0] if action_args else '')
            if status:
                # log activity in database
                a = Activity()
                a.type = Activity.get_type_id('Moved Draft' if t.is_draft else 'Moved Thought')
                a.author = request.user
                a.store_tokens({'title': t.title, 'slug': t.slug, 'old_idea': t_old_idea, 'new_idea': action_args[0]})
                a.url = reverse('dashboard-author') + "?id=" + t.slug
                a.save()

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': ''})
        elif action == 'thought_delete':
            t = Thought.objects.filter(slug=i)[0]
            t_idea = t.idea.slug
            status, tokens = thought_delete(i)

            if status:
                # log activity in database
                a = Activity()
                a.type = Activity.get_type_id('Deleted Draft' if t.is_draft else 'Deleted Thought')
                a.author = request.user
                a.store_tokens({'length': 1, 'title': t.title, 'idea': t_idea})
                a.url = reverse('dashboard-thoughts') + "?id=" + t_idea
                a.save()

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': ''})
        elif action == 'highlight_delete':
            h = Highlight.objects.filter(id=i)[0]
            h_title = h.title
            status, tokens = highlight_delete(i)
            if status:
                # log activity in database
                a = Activity()
                a.type = Activity.get_type_id('Deleted Highlight')
                a.author = request.user
                a.store_tokens({'title': h_title, 'id': i})
                a.url = reverse('dashboard-highlights')
                a.save()

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': ''})
        elif action == 'book_delete':
            b = ReadingListItem.objects.filter(id=i)[0]
            b_title = b.title
            status, tokens = book_delete(i)
            if status:
                # log activity in database
                a = Activity()
                a.type = Activity.get_type_id('Deleted Book')
                a.author = request.user
                a.store_tokens({'title': b_title, 'id': i})
                a.url = reverse('dashboard-books')
                a.save()

            fmm.add_message({'action': action, 'status': status, 'tokens': tokens, 'extra_html': ''})
        else:
            messages.add_message(request, messages.ERROR, "Unknown operation specified.")
            return redirect(next_url)

    fmm.flush_messages_to_user(request)
    return redirect(next_url)


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


@login_required(login_url='index')
def generate_upload_filename(request, filename, full_path=None):
    """ server call to calculate filename of uploaded file
    """
    filename = urllib.unquote(filename)
    filename = filename.replace('\\', os.sep)
    return JsonResponse(lib.generate_upload_filename(filename, full_path), safe=False)


@login_required(login_url='index')
def search_aws(request, keywords):
    """ REST request to Amazon Product Advertising API
    """
    try:
        max_len = lib.NUM_AMAZON_RESULTS
        if 'n' in request.GET and int(request.GET['n']) in range(lib.NUM_AMAZON_RESULTS):
            max_len = int(request.GET['n'])
    except (IndexError, ValueError):
        max_len = lib.NUM_AMAZON_RESULTS

    data = lib.Amazon().search(keywords=keywords, max_len=max_len)
    for d in data:
        for k, v in d.items():
            d[k] = urlquote_plus(v)

    return JsonResponse(data, safe=False)


###############################################################################
# helper functions
###############################################################################
def undo_button_html(request, input_data):
    """ return html string for undo button for use in a flash message. This
        html includes form data for reversing a server operation

        input data should be a dictionary that will be translated to a bunch of
        hidden input html elements (the key is the name and value is value)
    """
    undo_html = "<form action='%s' method='post'>" % reverse('dashboard-backend')
    undo_html += "<input type='hidden' name='csrfmiddlewaretoken' value='%s' />" % unicode(csrf(request)['csrf_token'])

    # gather id data from request
    if 'id' in request.POST:
        for item in request.POST.getlist('id'):
            undo_html += "<input type='hidden' name='id' value='%s' />" % lib.slugify(item)

    # obtain next url
    if 'next' in request.POST:
        next_url = request.POST['next']
    else:
        next_url = request.META['HTTP_REFERER']

    undo_html += "<input type='hidden' name='next' value='%s' />" % next_url

    # add extra input data
    for k, v in input_data.items():
        undo_html += "<input type='hidden' name='%s' value='%s' />" % (str(k), str(v))

    undo_html += "<button type='submit'>Undo</button>"
    undo_html += "</form>"

    return undo_html


def idea_safe_delete(idea_slug):
    """ delete a given idea (identified by idea_slug) only if it has no
        associated thoughts. Else do not delete and raise ValidationError
    """
    try:
        idea_slug = lib.slugify(idea_slug)
        idea = Idea.objects.get(slug=idea_slug)
        num_thoughts = Thought.objects.filter(idea=idea).count()

        if num_thoughts > 0:
            raise ValidationError("Cannot delete Idea: has associated thoughts")

        idea.delete()
    except (Exception, Idea.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'idea': idea_slug}


def idea_swap_order(idea_slug, adjacent_idea_slug):
    """ swap an idea with another given idea (based on the order column)

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a string containing an information log message
    """
    try:
        idea_slug = lib.slugify(idea_slug)
        adjacent_idea_slug = lib.slugify(adjacent_idea_slug)

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
    except (Exception, Idea.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'idea': idea_slug}


def thought_move(thought_slug, idea_slug):
    """ move a thought from one idea to another

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a dictionary containing string tokens
    """
    try:
        thought_slug = lib.slugify(thought_slug)
        idea_slug = lib.slugify(idea_slug)

        thought = Thought.objects.get(slug=thought_slug)
        idea = Idea.objects.get(slug=idea_slug)

        thought.idea = idea
        thought.save()
    except (Exception, Thought.DoesNotExist, Idea.DoesNotExist) as e:
        return False, {'error': e.message}

    return True, {'thought': thought_slug, 'idea': idea.name}


def thought_trash(thought_slug, trash=True):
    """ set the is_trash field on a given Thought.

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a string containing an information log message
    """
    try:
        thought_slug = lib.slugify(thought_slug)
        thought = Thought.objects.get(slug=thought_slug)

        thought.is_trash = trash
        thought.save()
    except (Exception, Thought.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'thought': thought_slug}


def thought_publish(thought_slug, publish=False, auto_update=False):
    """ Select a thought by the slug and change the is_draft field
        back to True. This takes the thought visibility out of the front page
        and idea detail page. Also, viewing the thought on its own page will
        require authentication of a logged in user.

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a string containing an information log message
    """
    try:
        thought_slug = lib.slugify(thought_slug)
        thought = Thought.objects.get(slug=thought_slug)
        thought.is_draft = not publish
        thought.save(auto_update=auto_update)
    except (Exception, Thought.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'thought': thought_slug, 'page': 'Drafts' if not publish else thought.idea.name}


def thought_delete(thought_slug):
    """ Delete a thought specified by thought_slug

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a dictionary containing string tokens
    """
    try:
        thought_slug = lib.slugify(thought_slug)
        thought = Thought.objects.get(slug=thought_slug)
        thought.delete()
    except (Exception, Thought.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'thought': thought_slug}


def highlight_delete(highlight_id):
    """ Delete a highlight specified by highlight_id

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a string containing an information log message
    """
    try:
        highlight_id = int(highlight_id)
        highlight = Highlight.objects.get(id=highlight_id)
        highlight_title = highlight.title
        highlight.delete()
    except (Exception, Highlight.DoesNotExist) as e:
        return False, {'highlight': highlight_id, 'error': e.message}
    return True, {'highlight_title': highlight_title, 'highlight_id': highlight_id}


def book_delete(book_id):
    """ Delete a book specified by a book_id

        returns a 2-tuple with the first element being a boolean (True on success, False on failure)
        and the second element being a string containing an information log message
    """
    try:
        book = ReadingListItem.objects.get(id=book_id)
        book_title = "'" + book.title + "'" + ' (#%d)' % book.id
        book.delete()
    except (Exception, ReadingListItem.DoesNotExist) as e:
        return False, {'error': e.message}
    return True, {'book_title': book_title}


def find_unique_slug(unsafe_slug, model):
    """ take a string and generate a slug using the lib.slugify function
        and make sure it does not collide with anything in the database

        specify a model to search for collisions against
    """
    test_slug = lib.slugify(unsafe_slug)

    collision_idx = 2
    while model.objects.filter(slug=test_slug).exists():
        test_slug = lib.slugify(unsafe_slug + "-" + str(collision_idx))
        collision_idx += 1
    return test_slug


def dashboard_stats():
    """ compile statistics from database and return a dictionary object.
    """
    stats = {
        'thought_count': Thought.objects.filter(is_draft=False, is_trash=False).count(),
        'draft_count': Thought.objects.filter(is_draft=True, is_trash=False).count(),
        'trash_count': Thought.objects.filter(is_trash=True).count(),
        'idea_count': Idea.objects.all().count(),
        'highlight_count': Highlight.objects.all().count(),
        'read_book_count': ReadingListItem.objects.filter(wishlist=False).count(),
        'wish_book_count': ReadingListItem.objects.filter(wishlist=True).count(),
        'total_book_count': ReadingListItem.objects.all().count(),
    }
    return stats


###############################################################################
# Form handling views
###############################################################################
class FormIdeaView(View):
    """ API endpoints for forms to manage user interaction for Ideas
    """
    def get(self, request):
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

    def post(self, request):
        """ save the POST data for the form into a new Idea

            request.POST['next'] optional url for redirect on completion
        """
        # make POST data mutable
        request.POST = request.POST.copy()

        # prepare activity to log in database
        activity = Activity()
        activity.author = request.user

        callback = None
        if 'next' in request.POST:
            callback = request.POST['next']

        # prevent accidental edit when writing new post with same slug
        if 'edit' in request.POST:
            slug = lib.slugify(request.POST['edit'])
        elif 'slug' in request.POST and request.POST['slug']:
            slug = find_unique_slug(request.POST['slug'], Idea)
        else:
            slug = find_unique_slug(request.POST['name'], Idea)
        request.POST['slug'] = slug

        try:
            instance = Idea.objects.get(slug=request.POST['slug'])
            msg = "Successfully edited Idea '%s'" % instance.name
            activity.type = Activity.get_type_id('Edited Idea')

            # keep track of idea icon
            if 'icon-clear' in request.POST and instance.icon:
                lib.delete_file(instance.icon.name)
            original_icon = instance.icon
        except Idea.DoesNotExist:
            instance = None
            original_icon = None
            activity.type = Activity.get_type_id('Create Idea')
            msg = "Successfully created Idea '%s'" % request.POST['name']

        idea_form = IdeaForm(request.POST, request.FILES, instance=instance)
        if idea_form.is_valid():
            idea = idea_form.save()

            activity.url = reverse('dashboard-thoughts') + "?id=" + request.POST['slug']
            activity.store_tokens({'name': request.POST['name'], 'slug': request.POST['slug']})
            activity.save()

            # delete old icon if necessary
            if original_icon and idea.icon and original_icon.name != idea.icon.name:
                lib.delete_file(original_icon.name)

            if callback:
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect(callback)
            return JsonResponse(serializers.serialize('json', [idea]), safe=False)
        else:
            errors = {}
            for field in idea_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(request.META['HTTP_REFERER'])
            else:
                return JsonResponse(errors)


class FormThoughtView(View):
    """ API endpoints for forms to manage user interactions and Thoughts
    """
    def get(self, request):
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

    def post(self, request):
        """ save the POST data to create a new Thought

            request.POST['next'] optional url for redirect on completion
            request.POST['edit'] slug of thought, signifies edit (leave key missing for new Thought)
        """
        # make POST data mutable
        request.POST = request.POST.copy()

        # start activity instance
        activity = Activity()
        activity.author = request.user

        # calculate next url
        callback = None
        if 'next' in request.POST:
            callback = lib.replace_tokens(request.POST['next'], {'idea': request.POST['idea']})

        # prevent accidental edit when writing new post with same slug
        if 'edit' in request.POST:
            slug = lib.slugify(request.POST['edit'])
        elif 'slug' in request.POST and request.POST['slug']:
            slug = find_unique_slug(request.POST['slug'], Thought)
        else:
            slug = find_unique_slug(request.POST['title'], Thought)
        request.POST['slug'] = slug

        # do some work on is_draft (connected to submit button values)
        if request.POST['is_draft'] == 'False':
            request.POST['is_draft'] = ''

        try:
            instance = Thought.objects.get(slug=slug)

            # log activity in database
            if request.POST['is_draft'] and instance.is_draft:
                activity.type = Activity.get_type_id('Edited Draft')
            else:
                activity.type = Activity.get_type_id('Edited Thought')

            # delete preview if someone checks clear
            if 'preview-clear' in request.POST and instance.preview:
                lib.delete_file(instance.preview.name)

            # keep track of images to see if we need to delete some later
            original_preview = instance.preview
            inline_images = [os.path.basename(i) for i in instance.get_image_urls()]
        except Thought.DoesNotExist:
            # received new thought request, create new Thought
            instance = None
            original_preview = None
            inline_images = []

            # determine whether we are saving a draft or publishing a thought (for Activity Feed)
            if request.POST['is_draft']:
                activity.type = Activity.get_type_id('Started Draft')
            else:
                activity.type = Activity.get_type_id('Published Thought')

            author = request.user  # need to populate this form data
            request.POST['author'] = author.id

        thought_form = ThoughtForm(request.POST, request.FILES, instance=instance)
        if thought_form.is_valid():
            thought = thought_form.save()

            activity.url = reverse('dashboard-author') + "?id=" + request.POST['slug']
            activity.store_tokens({'length': 1, 'title': request.POST['title']})
            activity.save()

            # check if new preview image is uploaded (or clear is checked) and delete old preview
            if original_preview and thought.preview and original_preview.name != thought.preview.name:
                lib.delete_file(original_preview.name)

            # check if we need to delete any inline images
            new_inline_images = [os.path.basename(i) for i in thought.get_image_urls()]
            for image in inline_images:
                if image not in new_inline_images:
                    lib.delete_file(os.path.join(paths.MEDIA_IMAGE_DIR, image))

            if callback:
                if request.POST['is_draft']:
                    messages.add_message(request, messages.WARNING, "Saved draft '%s' for later." % slug)
                elif 'edit' in request.POST:
                    messages.add_message(request, messages.SUCCESS, "Successfully edited Thought '%s'." % slug)
                else:
                    messages.add_message(request, messages.SUCCESS, "Successfully created Thought '%s'." % slug)

                return redirect(callback)
            return JsonResponse(serializers.serialize('json', [thought]), safe=False)
        else:
            errors = {}
            for field in thought_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(request.META['HTTP_REFERER'])
            return JsonResponse(errors)


class FormHighlightView(View):
    """ API endpoints for forms to manage user interactions and Links
    """
    def get(self, request):
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

    def post(self, request):
        """ Save POST data to create a new Link of the Day

            request.POST['next'] optional url for redirect on completion
        """
        # make POST data mutable
        request.POST = request.POST.copy()

        # create activity item
        activity = Activity()
        activity.author = request.user

        # calculate next url
        callback = None
        if 'next' in request.POST:
            callback = request.POST['next']

        # prevent accidental edit when writing new highlights with same slug
        if 'id' not in request.POST or not request.POST['id']:
            request.POST['id'] = -1

        try:
            instance = Highlight.objects.get(id=request.POST['id'])
            msg = "Successfully edited Highlight '%s'" % instance.title

            # log activity in database
            activity.type = Activity.get_type_id('Edited Highlight')

            # keep track of highlight icon
            if 'icon-clear' in request.POST and instance.icon:
                lib.delete_file(instance.icon.name)
            original_icon = instance.icon
        except Highlight.DoesNotExist:
            instance = None
            original_icon = None

            # log activity in database
            activity.type = Activity.get_type_id('Added New Highlight')

            msg = "Successfully created Highlight '%s'" % request.POST['title']

        highlight_form = HighlightForm(request.POST, request.FILES, instance=instance)
        if highlight_form.is_valid():
            highlight = highlight_form.save()
            activity.store_tokens({'title': request.POST['title'], 'id': highlight.id})
            activity.url = reverse('dashboard-highlights') + "?id=" + str(highlight.id)
            activity.save()

            # remove old icon file if necessary
            if original_icon and highlight.icon and original_icon.name != highlight.icon.name:
                lib.delete_file(original_icon.name)

            if callback:
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect(callback)
            else:
                return JsonResponse(serializers.serialize('json', [highlight]), safe=False)
        else:
            errors = {}
            for field in highlight_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(request.META['HTTP_REFERER'])
            return JsonResponse(errors)


class FormReadingListView(View):
    """ API endpoints to manage ReadingListItems
    """
    def get(self, request):
        form = ReadingListItemForm()
        form_html = form.as_table()

        if "output" in request.GET:
            if request.GET["output"] == "p":
                form_html = form.as_p()
            elif request.GET["output"] == "ul":
                form_html = form.as_ul()

        context = {'form': form_html}
        return JsonResponse(context)

    def post(self, request):
        # make POST data mutable
        request.POST = request.POST.copy()

        # calculate next url
        callback = None
        if 'next' in request.POST:
            callback = request.POST['next']

        # log activity in database
        activity = Activity()
        activity.author = request.user

        # prevent accidental edit when writing new reading list items
        if 'id' not in request.POST or not request.POST['id']:
            request.POST['id'] = -1

        try:
            instance = ReadingListItem.objects.get(id=request.POST['id'])
            msg = "Successfully edited Book List Item '%s'" % instance.title

            if instance.wishlist and 'wishlist' not in request.POST:
                activity.type = Activity.get_type_id('Moved Book to Recently Read List')
            else:
                activity.type = Activity.get_type_id('Edited Book')
        except ReadingListItem.DoesNotExist:
            instance = None
            msg = "Successfully created Book List Item '%s'" % request.POST['title']
            activity.type = Activity.get_type_id('Added Book to Wish List' if 'wishlist' in request.POST else 'Added Book to Recently Read List')

        reading_list_form = ReadingListItemForm(request.POST, instance=instance)
        if reading_list_form.is_valid():
            reading_list_item = reading_list_form.save()

            activity.store_tokens({'title': request.POST['title'], 'id': reading_list_item.id})
            activity.url = reverse('dashboard-books') + "?id=" + str(reading_list_item.id)
            activity.save()

            if callback:
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect(callback)
            else:
                return JsonResponse(serializers.serialize('json', [reading_list_item]), safe=False)
        else:
            errors = {}
            for field in reading_list_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(request.META['HTTP_REFERER'])
            else:
                return JsonResponse(errors)


class FormTaskView(View):
    """ API endpoints for server backend logic of Task models
    """
    def get(self, request):
        """ get html form for adding a new model instance
        """
        form = TaskForm()
        form_html = form.as_table()

        if "output" in request.GET:
            if request.GET["output"] == "p":
                form_html = form.as_p()
            elif request.GET["output"] == "ul":
                form_html = form.as_ul()

        context = {'form': form_html}
        return JsonResponse(context)

    def post(self, request):
        """ create a new Task Item
        """
        if not request.user.is_authenticated():
            return HttpResponseForbidden

        # make POST data mutable
        request.POST = request.POST.copy()

        # log activity in database
        activity = Activity()
        activity.author = request.user

        # calculate next url
        callback = None
        if 'next' in request.POST:
            callback = request.POST['next']

        if 'id' not in request.POST or not request.POST['id']:
            request.POST['id'] = -1

        try:
            instance = Task.objects.get(id=request.POST['id'])
            msg = "Successfully edited Task #%d" % instance.id
            activity.type = Activity.get_type_id('Edited Task Item')
        except Task.DoesNotExist:
            instance = None
            msg = "Successfully created new Task"
            activity.type = Activity.get_type_id('Added New Task Item')

        task_form = TaskForm(request.POST, instance=instance)
        if task_form.is_valid():
            task = task_form.save()

            activity.store_tokens({'id': task.id, 'content': task.content})
            activity.url = request.META['HTTP_REFERER']
            activity.save()

            if callback:
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect(callback)
            else:
                return JsonResponse(serializers.serialize('json', [task]), safe=False)
        else:
            errors = {}
            for field in task_form:
                errors[field.name] = field.errors

            if callback:
                msg = "<br>".join([k + ": " + " ".join(v) for k, v in errors.items() if v])
                messages.add_message(request, messages.ERROR, msg)
                return redirect(request.META['HTTP_REFERER'])
            else:
                return JsonResponse(errors)

    @staticmethod
    def mark_complete(request, id):
        """ mark a model instance as complete
        """
        if not request.user.is_authenticated():
            return HttpResponseForbidden

        try:
            id = int(id)
        except ValueError:
            msg = "Task'%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        try:
            task = Task.objects.filter(id=id)[0]
            task.is_completed = True
            task.save()

            # log activity in database
            activity = Activity()
            activity.author = request.user
            activity.type = Activity.get_type_id('Marked Task Item as Completed')
            activity.store_tokens({'id': task.id, 'content': task.content})
            activity.url = request.META['HTTP_REFERER']
            activity.save()

            msg = "Task '%s' marked complete." % id
            messages.add_message(request, messages.SUCCESS, msg)
        except Task.DoesNotExist:
            msg = "Task '%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        return redirect(request.META['HTTP_REFERER'])

    @staticmethod
    def change_priority(request, id, priority):
        """ change the priority of a Task
        """
        if not request.user.is_authenticated():
            return HttpResponseForbidden

        try:
            id = int(id)
            priority = int(priority)
            if priority not in [i for (i, d) in Task.PRIORITY]:
                raise ValueError("Invalid priority value '%d" % priority)
        except ValueError:
            msg = "Task '%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        try:
            task = Task.objects.filter(id=id)[0]

            old_priority = task.priority
            task.priority = priority
            task.save()

            # log activity in database
            activity = Activity()
            activity.author = request.user
            activity.type = Activity.get_type_id('Changed Task Priority')
            activity.store_tokens({'id': task.id, 'content': task.content, 'old_priority': old_priority, 'new_priority': priority})
            activity.url = request.META['HTTP_REFERER']
            activity.save()

            msg = "Changed Task #%d priority from %s to %s" %\
                  (task.id, Task.PRIORITY[old_priority][1], Task.PRIORITY[priority][1])
            messages.add_message(request, messages.SUCCESS, msg)
        except Task.DoesNotExist:
            msg = "Task '%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        return redirect(request.META['HTTP_REFERER'])

    @staticmethod
    def delete(request, id):
        """ delete a model instance
        """
        if not request.user.is_authenticated():
            return HttpResponseForbidden

        try:
            id = int(id)
        except ValueError:
            msg = "Task '%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        try:
            task = Task.objects.filter(id=id)[0]

            # log activity in database
            activity = Activity()
            activity.author = request.user
            activity.type = Activity.get_type_id('Deleted Task Item')
            activity.store_tokens({'id': task.id, 'content': task.content})
            activity.url = reverse('dashboard-todo')
            activity.save()

            msg = "Successfully deleted Task #%d" % task.id
            task.delete()

            messages.add_message(request, messages.SUCCESS, msg)
        except Task.DoesNotExist:
            msg = "Task '%s' does not exist." % id
            messages.add_message(request, messages.ERROR, msg)
            return redirect(request.META['HTTP_REFERER'])

        return redirect(request.META['HTTP_REFERER'])