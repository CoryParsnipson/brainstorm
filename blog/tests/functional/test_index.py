from django.test import TestCase

from selenium import webdriver


class TestIndex(TestCase):
    """ web browser level tests for all functions related to the index page
    """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_index_title(self):
        """ open a browser in Firefox and check to see if the title is correct
        """
        self.browser.get('http://localhost')
        self.assertIn('SP', self.browser.title)