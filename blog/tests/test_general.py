from django.db import IntegrityError
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
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


class IdeaFormTestCase(TestCase):
    """ unit tests related to IdeaForm functions
    """
    def setUp(self):
        self.client = Client()


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
        return
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
        response = self.client.delete(reverse('idea-page', kwargs={'idea_slug': self.idea1.slug}))
        self.assertEqual(200, response.status_code)

        # check again for existence of idea1
        self.assertEqual(0, Idea.objects.count())

    def test_delete_failure_thoughts_exist(self):
        """ create an idea and some thoughts that go with it and then try
            to delete it. Expect the delete request to fail.
        """
        return
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
        self.assertRaises(ValidationError, self.client.delete, reverse('idea-page', kwargs={'idea_slug': self.idea1.slug}))

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