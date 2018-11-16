from django import template
from django.core.urlresolvers import reverse
from django.utils.dateformat import DateFormat
from django.utils.html import format_html

from blog import lib
from blog.models import Idea, ReadingListItem, Task, Note
from blog.views import dashboard_stats

register = template.Library()


class TemplateTaskList(template.Node):
    def __init__(self, name='tasks', task_list_length=lib.NUM_TASK_LIST, idea=None):
        self.name = name
        self.length = task_list_length
        self.idea = idea

    def render(self, context):
        tasks = Task.objects.filter(is_completed=False)

        if self.idea:
            idea = template.Variable(self.idea).resolve(context)
            if idea:
                tasks = tasks.filter(idea=idea)

        context[self.name] = Task.reorder_child_tasks(tasks)[:self.length]
        return ''


class TemplateNoteList(template.Node):
    """ template class to query for Notes
    """
    def __init__(self, name='notes', note_list_length=lib.NUM_NOTE_LIST, idea=None, thought=None):
        self.name = name
        self.length = max(0, note_list_length)
        self.idea = template.Variable(idea) if idea else None
        self.thought = template.Variable(thought) if thought else None

    def render(self, context):
        filter_args = {}

        if self.idea:
            filter_args['ideas'] = self.idea.resolve(context)

        thought_related_notes = []
        if self.thought:
            thought = self.thought.resolve(context)
            thought_related_notes = Note.objects.filter(thoughts=thought).order_by("-date_published")[:self.length]

        remaining_spots = max(0, self.length - len(thought_related_notes))
        idea_related_notes = Note.objects.filter(**filter_args).order_by("-date_published")[:remaining_spots]
        context[self.name] = list(thought_related_notes) + list(idea_related_notes)
        return ''


@register.tag
def get_latest_tasks(parser, token):
    """ return a list of tasks and work them into the template context

        parameters:
          kwargs['length'] -> number of tasks to return (ordered by
            priority and date added)
          kwargs['name'] -> value to store tasks in context variable
    """
    token_data = token.split_contents()
    token_data = token_data[1:]  # index 0 is tag name
    tokens = dict([tuple(l.split("=")) for l in token_data])

    try:
        tokens['name'] = tokens['name'].replace("'", "")
        tokens['length'] = int(tokens['length'])
    except KeyError:
        pass

    if 'idea' not in tokens:
        tokens['idea'] = None

    return TemplateTaskList(tokens['name'], task_list_length=tokens['length'], idea=tokens['idea'])


@register.tag
def get_latest_notes(parser, token):
    """ return a list of notes and work them into the template context

        parameters:
          kwargs['length'] -> number of notes to return (ordered by date
            published)
          kwargs['name'] -> value to store tasks in context variable
    """
    token_data = token.split_contents()
    token_data = token_data[1:]  # index 0 is tag name
    tokens = dict([tuple(l.split("=")) for l in token_data])

    try:
        tokens['name'] = tokens['name'].replace("'", "")
        tokens['length'] = int(tokens['length'])

        if 'idea' not in tokens:
            tokens['idea'] = None

        if 'thought' not in tokens:
            tokens['thought'] = None
    except KeyError:
        pass

    return TemplateNoteList(name=tokens['name'], note_list_length=tokens['length'], idea=tokens['idea'], thought=tokens['thought'])


@register.simple_tag
def idea_dropdown(**kwargs):
    """ spit out a dropdown list of ideas; this is basically a form widget

        Parameters:
        kwargs['dropdown_classes'] -> classes to append to dropdown ul
        kwargs['action'] -> name of the li buttons in dropdown ul
    """
    dropdown_classes = kwargs['dropdown_classes'] if 'dropdown_classes' in kwargs else ''
    action = kwargs['action'] if 'action' in kwargs else ''
    ideas = Idea.objects.all().order_by('order')

    dropdown_html = format_html(
        "<ul class='dropdown{}'>",
        ' ' + dropdown_classes
    )

    for idea in ideas:
        li_name = " name=%s" % (action or 'idea_dropdown')
        dropdown_html += format_html(
            "<li><button type='submit'{} value='{}'>{}</button></li>",
            li_name,
            "thought_idea_move|" + idea.slug,
            idea.name
        )

    dropdown_html += format_html("</ul>")
    return dropdown_html


@register.simple_tag
def thought_nav(thought, **kwargs):
    """ takes a "current thought" object and enumerates adjacent thoughts on
        the page.

        Parameters:
        kwargs['direction'] -> 'next' or 'prev'
        kwargs['length'] -> maximum number of thoughts in direction to pull
        kwargs['header'] -> text to display in header above thoughts
        kwargs['blockgridclass'] -> classes of ul block grid
    """
    header = kwargs['header'] if 'header' in kwargs else 'Thoughts'
    direction = kwargs['direction'] if 'direction' in kwargs else 'next'
    length = kwargs['length'] if 'length' in kwargs else 1
    block_grid_class = kwargs['blockgridclass'] if 'blockgridclass' in kwargs else 'small-block-grid-1'
    placeholder_html = format_html("<div class='nav-placeholder'><p>&nbsp;</p><span>SP</span></div>")

    list_html = format_html("<ul class='{} thought-nav'>", block_grid_class)
    list_html += format_html("<li><div class='header strong'>{}</div></li>", header)

    if not thought:
        list_html += format_html("<li>{}</li></ul>", placeholder_html)
        return list_html

    if direction == 'next':
        adj_thoughts = reversed(thought.get_next_thoughts(num=length))
    else:
        adj_thoughts = thought.get_prev_thoughts(num=length)

    for t in adj_thoughts:
        if not t:
            list_html += format_html("<li>{}</li>", placeholder_html)
        else:
            list_html += format_html(
                "<li><div class='nav'><a class='overlay' href='{}'></a><p>{}</p><img src='{}' /></div></li>",
                reverse('thought-page', kwargs={'idea_slug': t.idea.slug, 'thought_slug': t.slug}),
                t.title,
                t.get_preview(),
            )

    list_html += format_html("</ul>")
    return list_html


@register.filter()
def rev(value, args=''):
    kwargs = {}
    if args:
        arg_list = [arg.strip() for arg in args.split(',')]
        for pair in arg_list:
            k, v = pair.split('=')
            kwargs[k] = v

    return reverse(value, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def url_qs(context, **kwargs):
    """ takes the current url and query string from the request context
        and accepts named arguments and constructs a complete url string
        with the query string parameters cleaned swapped out with the
        named arguments.

        NOTE: needs 'django.template.context_processors.request' under the settings
        variable TEMPLATES.OPTIONS.context_processors

        e.g.) request.path -> http://www.slackerparadise.com/ideas
              request.META.QUERY_STRING -> idea=miscellaneous&p=4
              kwargs -> { 'p' : 23 }

              returns ->
              http://www.slackerparadise.com/ideas?idea=miscellaneous&p=23
    """
    request = context['request']

    # get query string parameters
    params = {}
    for pair in request.META['QUERY_STRING'].split("&"):
        parts = pair.split("=")
        if not parts:
            continue

        if len(parts) >= 2:
            key, value = parts[0], parts[1]
        else:
            key, value = parts[0], ''

        if not key:
            continue

        params[str(key)] = str(value)

    # add/replace query string parameters in kwargs
    for kwarg, value in kwargs.items():
        params[str(kwarg)] = str(value)

    query_string = "&".join([k + "=" + v for k, v in params.items()])
    if query_string:
        query_string = '?' + query_string

    return request.path + query_string


@register.simple_tag
def recently_read(**kwargs):
    """ return html containing data from the recently read list
        Specify an argument n=[int] to determine how many entries
        are rendered in the list.
    """
    num_entries = int(kwargs['n']) if 'n' in kwargs else lib.NUM_READ_LIST
    read_list = ReadingListItem.objects.filter(wishlist=False).order_by('-date_published')[:num_entries]

    list_html = format_html("<h3>Recently Read</h3><div class=\"book-list\">")
    for book in read_list:
        list_html += format_html("<div class='book-book-result book-book-result-hover group'>")
        list_html += format_html("<img src='{}' class='left'>", book.cover)
        list_html += format_html("<p class='title'>{}</p>", book.title)
        list_html += format_html("<p class='author'>{}</p>", book.author)
        list_html += format_html("<p class='description'>{}</p>", book.description)

        dt = DateFormat(book.date_published)
        list_html += format_html("<p class='date'>Added on {}</p>", dt.format("F j, Y g:i A"))

        if book.favorite:
            list_html += format_html("<span class='favorite' title='Cory\'s Favorites'>&#x2605;</span>")

        list_html += format_html("<a class='overlay' href='{}' target='_blank'></a></div>", book.link)

    if len(read_list) == 0:
        list_html += format_html("<p class='empty'>Cory hasn't read any books yet!</p>")

    list_html += format_html("<p class='empty'><a href='{}'>(See More)</a></p></div>", reverse('books'))
    return list_html


@register.simple_tag(takes_context=True)
def stat_box(context):
    """ creates a stat box "widget"
    """

    # stats are only for logged in users
    if not context['request'].user.is_authenticated():
        return

    stats = dashboard_stats()
    list_html = format_html("<div class='stat-box'>")
    list_html += format_html("<h3>Stats</h3>")

    list_html += format_html("<p class='green'>")
    list_html += format_html("<a href='{}'>Ideas</a>:<span class='right'>{}</span>", reverse('dashboard-ideas'), stats['idea_count'])
    list_html += format_html("</p>")

    list_html += format_html("<p class='purple'>")
    list_html += format_html("<a href='{}'>Thoughts</a>:<span class='right'>{}</span>", reverse('dashboard-thoughts'), stats['thought_count'])
    list_html += format_html("</p>")

    list_html += format_html("<p class='blue'>")
    list_html += format_html("<a href='{}'>Drafts</a>:<span class='right'>{}</span>", reverse('dashboard-drafts'), stats['draft_count'])
    list_html += format_html("</p>")

    list_html += format_html("<p class='red'>")
    list_html += format_html("<a href='{}'>Trash</a>:<span class='right'>{}</span>", reverse('dashboard-trash'), stats['trash_count'])
    list_html += format_html("</p>")

    list_html += format_html("<p class='orange'>")
    list_html += format_html("<a href='{}'>Highlights</a>:<span class='right'>{}</span>", reverse('dashboard-highlights'), stats['highlight_count'])
    list_html += format_html("</p>")

    list_html += format_html("<p class='yellow'>")
    list_html += format_html("<a href='{}'>Books</a>:", reverse('dashboard-books'))
    list_html += format_html("<span class='right grey'>")
    list_html += format_html("<span class='green'>W-</span>{}&nbsp;", stats['wish_book_count'])
    list_html += format_html("<span class='red'>R-</span>{}&nbsp;", stats['read_book_count'])
    list_html += format_html("<span class='purple'>T-</span>{}", stats['total_book_count'])
    list_html += format_html("</span>")
    list_html += format_html("</p>")

    list_html += format_html("</div>")

    return list_html
