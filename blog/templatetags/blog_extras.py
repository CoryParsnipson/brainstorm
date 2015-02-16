from django import template

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