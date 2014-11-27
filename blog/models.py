from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Idea(models.Model):
    """ In other blogs, this would be called a "Category", but I want to
        connote a sense of progression on a line of inquiry or research. For
        instance, an Idea could be a "video game idea" and Thoughts
        associated with the Idea would be progress/status updates containing
        maybe screen shots, videos, and even code snippets.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(primary_key=True)
    description = models.TextField()
    # color?
    # icon?

    def __unicode__(self):
        return self.name


class Thought(models.Model):
    """ Thought class corresponds roughly to a blog post. The intention
        is to have many child classes of Thought to include different types
        of multimedia. For example, posts in a "comic" idea would ideally
        contain one required comic picture along with a relatively short
        text description.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(primary_key=True)
    content = models.TextField()
    idea = models.ForeignKey(Idea)
    author = models.ForeignKey(User)
    date_published = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, auto_now_add=True)