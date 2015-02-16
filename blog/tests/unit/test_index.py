from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from django.http import HttpRequest

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
    def test_valid_html(self):
        """ make sure a valid html document is returned for index
        """
        request = HttpRequest()
        response = views.index(request)

        # TODO: more complex text matching?
        self.assertTrue(response.content.startswith(r'<!DOCTYPE html>'))
        self.assertTrue(response.content.endswith('</html>'))