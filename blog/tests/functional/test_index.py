from django.test import TestCase

from selenium import webdriver


class TestIndex(TestCase):
    """ web browser level tests for all functions related to the index page
    """

    def setUp(self):
        self.browser = {
            'ff': webdriver.Firefox(),
            #'chr': webdriver.Chrome(),
            #'ie': webdriver.Ie(),
            #'o': webdriver.Opera(),
        }

    def tearDown(self):
        for n, b in self.browser.items():
            b.quit()

    def test_index_title(self):
        """ open a browser in Firefox and check to see if the title is correct
        """
        for n, b in self.browser.items():
            b.get('http://localhost')
            self.assertIn('SP', b.title)