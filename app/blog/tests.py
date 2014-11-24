from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from blog.models import Idea, Thought


# Create your tests here.
class ThoughtBasicTestCase(TestCase):
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

    def test_(self):
        pass