from django.test import TestCase

from blog.models import Idea


class Test(TestCase):

    def test_idea(self):
        ideas = Idea.objects.all()
        #self.assertEqual(1, len(ideas))