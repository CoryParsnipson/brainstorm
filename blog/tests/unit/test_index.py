from django.core.urlresolvers import resolve, reverse
from django.test import TestCase

import blog.views as views


class TestIndex(TestCase):
    """ unit tests related to index page
    """

    def test_reverse(self):
        """ preserve named url value
        """
        self.assertEqual(reverse('index'), '/')

    def test_resolve(self):
        """ preserve uri to view function mapping
        """
        self.assertEqual(views.index, resolve('/').func)