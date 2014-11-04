from django.test import TestCase
from django.contrib.auth.models import User

from blog.models import Idea, Thought


# Create your tests here.
class ThoughtTestCase(TestCase):
    def setUp(self):
        author = User.objects.create(username="Cory", email="cparsnipson@gmail.com", password="test")

        idea = Idea.objects.create(name="Miscellaneous",
                                   description="Random, blog thoughts.")

        Thought.objects.create(title='My First Thought',
                               slug='my-first-thought',
                               content='ugububughgagahh',
                               idea=idea,
                               author=author)

    def test_null(self):
        pass