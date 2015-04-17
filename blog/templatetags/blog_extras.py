from django import template
from django.core.urlresolvers import reverse
from django.utils.dateformat import DateFormat

from blog import lib
from blog.models import Idea, ReadingListItem, Task
from blog.views import dashboard_stats

register = template.Library()


class TemplateTaskList(template.Node):
    def __init__(self, name='tasks', task_list_length=lib.NUM_TASK_LIST, idea=''):
        self.name = name
        self.length = task_list_length
        self.idea = idea

    def render(self, context):
        tasks = Task.objects.filter(is_completed=False)

        if self.idea:
            idea = template.Variable(self.idea)
            tasks = tasks.filter(idea=idea.resolve(context))

        context[self.name] = tasks.order_by("-priority", "-date_added")[:self.length]
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
        tokens['idea'] = ''

    return TemplateTaskList(tokens['name'], task_list_length=tokens['length'], idea=tokens['idea'])


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

    dropdown_html = "<ul class='dropdown%s'>" % (' ' + dropdown_classes)

    for idea in ideas:
        li_name = " name='%s'" % (action or 'idea_dropdown')
        dropdown_html += "<li><button type='submit'%s value='%s'>%s</button></li>" % (li_name, "thought_idea_move|" + idea.slug, idea.name)

    dropdown_html += "</ul>"
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
    placeholder_html = "<div class='nav-placeholder'><p>&nbsp;</p><span>SP</span></div>"

    list_html = "<ul class='%s thought-nav'>" % block_grid_class
    list_html += "<li><div class='header strong'>%s</div></li>" % header

    if not thought:
        list_html += "<li>" + placeholder_html + "</li></ul>"
        return list_html

    if direction == 'next':
        adj_thoughts = reversed(thought.get_next_thoughts(num=length))
    else:
        adj_thoughts = thought.get_prev_thoughts(num=length)

    for t in adj_thoughts:
        if not t:
            list_html += "<li>" + placeholder_html + "</li>"
        else:
            url = reverse('thought-page', kwargs={'idea_slug': t.idea.slug, 'thought_slug': t.slug})

            list_html += "<li><div class='nav'>"
            list_html += "<a class='overlay' href='%s'></a>" % url
            list_html += "<p>%s</p>" % t.title
            list_html += "<img src='%s' />" % t.get_preview()
            list_html += "</div></li>"

    list_html += "</ul>"
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

        NOTE: needs 'django.core.context_processors.request' under the settings
        variable TEMPLATE_CONTEXT_PROCESSORS

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

    list_html = "<h3>Recently Read</h3><div class=\"book-list\">"
    for book in read_list:
        list_html += "<div class='aws-book-result aws-book-result-hover group'>"
        list_html += "<img src='%s' class='left'>" % book.cover
        list_html += "<p class='title'>%s</p>" % book.title
        list_html += "<p class='author'>%s</p>" % book.author
        list_html += "<p class='description'>%s</p>" % book.description

        dt = DateFormat(book.date_published)
        list_html += "<p class='date'>Added on %s</p>" % dt.format("F j, Y g:i A")

        if book.favorite:
            list_html += "<span class='favorite' title='Cory\'s Favorites'>&#x2605;</span>"

        list_html += "<a class='overlay' href='%s' target='_blank'></a>" % book.link
        list_html += "</div>"

    if len(read_list) == 0:
        list_html += "<p class='empty'>Cory hasn't read any books yet!</p>"

    list_html += "<p class='empty'><a href='%s'>(See More)</a></p>" % reverse('books')
    list_html += "</div>"

    return list_html


@register.simple_tag(takes_context=True)
def stat_box(context):
    """ creates a stat box "widget"
    """

    # stats are only for logged in users
    if not context['request'].user.is_authenticated():
        return

    stats = dashboard_stats()
    list_html = "<div class='stat-box'>"
    list_html += "<h3>Stats</h3>"

    list_html += "<p class='green'>"
    list_html += "<a href='%s'>Ideas</a>:<span class='right'>%s</span>" % (reverse('dashboard-ideas'), stats['idea_count'])
    list_html += "</p>"

    list_html += "<p class='purple'>"
    list_html += "<a href='%s'>Thoughts</a>:<span class='right'>%s</span>" % (reverse('dashboard-thoughts'), stats['thought_count'])
    list_html += "</p>"

    list_html += "<p class='blue'>"
    list_html += "<a href='%s'>Drafts</a>:<span class='right'>%s</span>" % (reverse('dashboard-drafts'), stats['draft_count'])
    list_html += "</p>"

    list_html += "<p class='red'>"
    list_html += "<a href='%s'>Trash</a>:<span class='right'>%s</span>" % (reverse('dashboard-trash'), stats['trash_count'])
    list_html += "</p>"

    list_html += "<p class='orange'>"
    list_html += "<a href='%s'>Highlights</a>:<span class='right'>%s</span>" % (reverse('dashboard-highlights'), stats['highlight_count'])
    list_html += "</p>"

    list_html += "<p class='yellow'>"
    list_html += "<a href='%s'>Books</a>:" % reverse('dashboard-books')
    list_html += "<span class='right grey'>"
    list_html += "<span class='green'>W-</span>%s&nbsp;" % stats['wish_book_count']
    list_html += "<span class='red'>R-</span>%s&nbsp;" % stats['read_book_count']
    list_html += "<span class='purple'>T-</span>%s" % stats['total_book_count']
    list_html += "</span>"
    list_html += "</p>"

    list_html += "</div>"

    return list_html
