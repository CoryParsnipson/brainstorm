from django.test import TestCase

from selenium import webdriver


class TestIndex(TestCase):
    """ web browser level tests for all functions related to the index page
    """

    def test_index_title(self):
        """ open a browser in Firefox and check to see if the title is correct
        """
        browser = webdriver.Firefox()
        browser.get('http://localhost')

        # browser title should have the correct appellation
        assert 'SP' in browser.title

        browser.quit()