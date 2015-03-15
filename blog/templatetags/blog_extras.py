from django import template
from django.core.urlresolvers import reverse
from django.utils.dateformat import DateFormat

from blog import lib
from blog.models import ReadingListItem
from blog.views import dashboard_stats

register = template.Library()


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
