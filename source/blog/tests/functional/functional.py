import sys

from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class FunctionalTestCase(StaticLiveServerTestCase):
    """ inherited class of StaticLiveServerTestCase that contains the ability
        to accept a commandline argument to point to a live website
        instead of using the static live server from the test framework.
        The variable live_server_url from StaticLiveServerTestCase is
        replaced with server_url (basically, use this instead).

        Usage: python manage.py test liveserver=[site]

        Note: this is taken from O'Reilly's TDD with Python book
    """

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                url_arg = arg.split('=')[1]
                if not url_arg.startswith('http://'):
                    cls.server_url = 'http://'
                cls.server_url += url_arg
                return

        super(FunctionalTestCase, cls).setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super(FunctionalTestCase, cls).tearDownClass()