import datetime

from django.db import IntegrityError
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import lib
from models import Idea, Thought


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
            args['is_draft'] = False  # just publish these right off the bat
            args['is_trash'] = False  # assume none are trashed for now

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
        """ get a list of all thoughts written by a specific author
        """
        num_expected = len(Thought.objects.filter(author=self.dummy_author2))
        test_url = reverse('thought-list') + "?author=" + str(self.dummy_author2.id)

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)

        for d in response.data:
            self.assertEqual(self.dummy_author2.id, d['author'])

    def test_list_by_author_null(self):
        """ get a list of all thoughts written by a specific author. There
            will be no results returned (should not fail)
        """
        num_expected = len(Thought.objects.filter(author=-1))
        test_url = reverse('thought-list') + "?author=-1"

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)
        self.assertEqual(num_expected, 0)

    def test_exclude(self):
        """ get a list of thoughts NOT by dummy_author1
        """
        num_expected = len(Thought.objects.filter(author=2))
        test_url = reverse('thought-list') + "?exclude=true&author=1"

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        num_received = len(response.data)
        self.assertEqual(num_received, num_expected)

        for d in response.data:
            self.assertEqual(d['author'], self.dummy_author2.id)


class IdeaFormTestCase(TestCase):
    """ unit tests related to IdeaForm functions
    """
    def setUp(self):
        self.client = Client()


class SlugifyTestCase(TestCase):
    """ unit tests related to slugify contents
    """

    def test_slugify_text_only(self):
        """ test slugify
        """
        test_string = "This is a test string."

        expected = "this-is-a-test-string"
        received = lib.slugify(test_string)

        self.assertEqual(expected, received)

    def test_slugify_truncate(self):
        """ test slugify that should truncate to 20 characters
        """
        test_string = "omg this is such a long string it will deinitely be truncated"

        expected = "omg-this-is-such-a-long"
        received = lib.slugify(test_string, max_len=20)

        self.assertEqual(expected, received)

    def test_slugify_alphanumeric(self):
        pass


class IdeaViewTestCase(TestCase):
    """ unit tests related to Idea view functions
    """

    def setUp(self):
        self.client = Client()

        # create superuser with permission to delete
        self.user = User.objects.create_superuser(
            username='Cory',
            email='cparsnipson@gmai.com',
            password='test'
        )
        self.user.save()

    def test_delete_success(self):
        # create sample idea in test database
        self.idea1 = Idea.objects.create(
            name="Idea1",
            slug="idea-1",
            description="This is Idea 1.",
            order=1
        )
        self.idea1.save()

        self.client.login(username='Cory', password='test')

        # send delete request
        response = self.client.delete(reverse('idea-detail', kwargs={'slug': self.idea1.slug}))
        self.assertEqual(200, response.status_code)

        # check again for existence of idea1
        self.assertEqual(0, Idea.objects.count())

    def test_delete_failure_thoughts_exist(self):
        """ create an idea and some thoughts that go with it and then try
            to delete it. Expect the delete request to fail.
        """
        # create sample idea in test database
        self.idea1 = Idea.objects.create(
            name="Idea1",
            slug="idea-1",
            description="This is Idea 1.",
            order=1
        )
        self.idea1.save()

        num_ideas = Idea.objects.count()

        # create some sample thoughts
        self.thought1 = Thought.objects.create(
            title="Thought1",
            slug="thought-1",
            content="This is Thought 1.",
            idea=self.idea1,
            author=self.user,
        )

        self.client.login(username='Cory', password='test')
        self.assertRaises(ValidationError, self.client.delete, reverse('idea-detail', kwargs={'slug': self.idea1.slug}))

        self.assertEqual(num_ideas, Idea.objects.count())


class FileUploadTestCase(TestCase):
    """ test file upload functions
    """
    def setup(self):
        self.client = Client()

        # create superuser with permission to delete
        self.user = User.objects.create_superuser(
            username='Cory',
            email='cparsnipson@gmai.com',
            password='test'
        )
        self.user.save()

    def test_file_upload(self):
        """ upload a file
        """

        self.client.login(username='Cory', password='test')
        response = self.client.post(reverse('upload'), )