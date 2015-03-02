from django.core.urlresolvers import resolve, reverse
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.test import TestCase

import blog.views as views


class TestIndex(TestCase):
    """ unit tests related to index page
    """

    ###########################################################################
    # url
    ###########################################################################
    def test_reverse(self):
        """ preserve named url value
        """
        self.assertEqual(reverse('index'), '/')

    def test_resolve(self):
        """ preserve uri to view function mapping
        """
        self.assertEqual(views.index, resolve('/').func)

    ###########################################################################
    # view
    ###########################################################################
    def test_correct_page(self):
        """ make sure a valid html document is returned for index
        """
        request = HttpRequest()
        response = views.index(request)

        expected_html = render_to_string('blog/index.html')
        self.assertEqual(response.content.decode(), expected_html)