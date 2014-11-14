from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Idea(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField()
    # color?
    # icon?

    def __unicode__(self):
        return self.name


class Thought(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = models.TextField()
    idea = models.ForeignKey(Idea)
    author = models.ForeignKey(User)
    date_published = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, auto_now_add=True)
    # category?