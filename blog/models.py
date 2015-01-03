import re

from django.db import models
from django.db.models import Max
from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    ordering = models.IntegerField(unique=True, null=True)
    # color?
    # icon?

    def __unicode__(self):
        return self.name


@receiver(pre_save)
def pre_save_idea(sender, instance, *args, **kwargs):
    """ pre save callback for Idea model. Used to autofill ordering for newly
        created Idea instances (or existing ones that don't have ordering for
        whatever reason).
    """
    if not isinstance(instance, Idea):
        return

    if not instance.ordering:
        next_ordering = Idea.objects.all().aggregate(Max('ordering'))['ordering__max']
        instance.ordering = 1 if not next_ordering else next_ordering + 1


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
    is_draft = models.BooleanField(default=True)
    is_trash = models.BooleanField(default=False)
    date_published = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, auto_now_add=True)


def slugify(source_str, max_len=20):
    """ create a nice slug given a string; FYI, Django comes with a prebuilt
        slugify function (django.template.defaultfilters) which handles
        non-unicode characters too, but doesn't truncate.

    :param source_str: string to make slug out of
    :param max_len: maximum length of slug
    :return: a string that is a valid slug
    """
    urlenc_regex = re.compile(r'[^a-z0-9\-_]+')
    str_words = source_str.lower().split(" ")

    counted_len = len(str_words[0])
    slug_tokens = [str_words.pop(0)]
    while str_words and counted_len + len(str_words[0]) <= max_len:
        counted_len += len(str_words[0])
        slug_tokens.append(str_words.pop(0))

    slug = "-".join(slug_tokens)
    slug = urlenc_regex.sub('', slug)
    return slug