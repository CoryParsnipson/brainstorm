import datetime

from django.db import IntegrityError
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from blog.models import Idea, Thought


# Create your tests here.
class ThoughtModelTestCase(TestCase):
    """ Unit tests for the Thought model.
    """
    def setUp(self):
        # create a dummy author object to sign thoughts
        self.dummy_author = User.objects.create(username="Cory",
                                                email="cparsnipson@gmail.com",
                                                password="test")

        # create an idea to attach thoughts to
        self.dummy_idea = Idea.objects.create(name="Miscellaneous",
                                              description="Random, blog thoughts.")

    def test_create_thought(self):
        """ Create a Thought object using the dummy author and dummy idea.
            Check to see if the thought was created without exception.
        """
        kwargs = {}
        kwargs['title'] = 'Thought 1'
        kwargs['slug'] = 'thought-1'
        kwargs['content'] = 'Contents of Thought 1.'
        kwargs['idea'] = self.dummy_idea
        kwargs['author'] = self.dummy_author

        try:
            thought = Thought.objects.create(**kwargs)
        except Exception as e:
            self.fail(e.message)

        self.assertIsInstance(thought, Thought)

    def test_unique_slug(self):
        """ Create two thought objects with identical slug values. Check for
            django.db.IntegrityError
        """
        kwargs1 = {}
        kwargs1['title'] = 'Thought 1'
        kwargs1['slug'] = 'thought-1'
        kwargs1['content'] = 'Contents of Thought 1.'
        kwargs1['idea'] = self.dummy_idea
        kwargs1['author'] = self.dummy_author

        kwargs2 = {}
        kwargs2['title'] = 'Thought 2'
        kwargs2['slug'] = 'thought-1'
        kwargs2['content'] = 'Contents of Thought 2.'
        kwargs2['idea'] = self.dummy_idea
        kwargs2['author'] = self.dummy_author

        try:
            thought1 = Thought.objects.create(**kwargs1)
            thought2 = Thought.objects.create(**kwargs2)
        except IntegrityError as e:
            self.assertEqual(e.message, "column slug is not unique")


class ThoughtViewTestCase(TestCase):
    """ Unit tests for views related to Thought
    """
    def setUp(self):
        """ setup a Django client fixture for testing views
        """
        self.client = Client()

        # create a dummy author object to sign thoughts
        self.dummy_author1 = User.objects.create(username="Cory",
                                                 email="cparsnipson@gmail.com",
                                                 password="test")

        self.dummy_author2 = User.objects.create(username="Angel",
                                                 email="abunny@gmail.com",
                                                 password="2cul4u")

        # create an idea to attach thoughts to
        self.dummy_idea1 = Idea.objects.create(name="Idea1",
                                               slug="idea1",
                                               description="First Idea")

        self.dummy_idea2 = Idea.objects.create(name="Idea2",
                                               slug="idea2",
                                               description="Second Idea")

        self.num_thoughts = 10
        args = {}

        # create sample thoughts
        for i in range(self.num_thoughts):
            args['title'] = 'Thought %d' % i
            args['slug'] = 'thought-%d' % i
            args['content'] = 'This is thought %d' % i
            args['date_published'] = datetime.datetime(2014, 11, 24, 0, 0) + datetime.timedelta(i)

            if self.num_thoughts / 2 > i:
                args['idea'] = self.dummy_idea1
            else:
                args['idea'] = self.dummy_idea2

            if i % 2 == 0:
                args['author'] = self.dummy_author1
            else:
                args['author'] = self.dummy_author2

            thought = Thought.objects.create(**args)
            thought.save()

    def test_list_no_params(self):
        """ get a list of all thoughts (no query params) and see if status is
            200 and all thoughts are returned
        """
        response = self.client.get(reverse('thought-list'))
        self.assertEqual(response.status_code, 200)

        num_thoughts_expected = len(Thought.objects.all())
        num_thoughts_received = len(response.data)

        self.assertEqual(num_thoughts_expected, num_thoughts_received)

    def test_list_by_idea(self):
        """ get a list of all thoughts with a specific idea and see if
            the returned input is correct
        """
        num_expected = len(Thought.objects.filter(idea=self.dummy_idea1))
        test_url = reverse('thought-list') + "?idea=" + self.dummy_idea1.slug

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)

        for d in response.data:
            self.assertEqual(d['idea'], self.dummy_idea1.slug)

    def test_list_by_idea_null(self):
        """ get a list of all thoughts with a specific idea. There will
            be no results returned (should not fail)
        """
        num_expected = len(Thought.objects.filter(idea='doesntexist'))
        test_url = reverse('thought-list') + "?idea=doesntexist"

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)
        self.assertEqual(num_expected, 0)

    def test_list_by_author(self):
        """ get a list of all thoughts written by specific author
        """
        num_expected = len(Thought.objects.filter(author=self.dummy_author2))
        test_url = reverse('thought-list') + "?author=" + str(self.dummy_author2.id)

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)

        for d in response.data:
            self.assertEqual(self.dummy_author2.id, d['author'])