import re
import datetime

import bleach

from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User


###############################################################################
# Idea model
###############################################################################
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
    order = models.IntegerField(unique=True)

    # color?
    # icon?

    def get_next(self):
        """ get the next Idea by order column or return
            None if this Idea instance is the latest
        """
        try:
            return Idea.objects.filter(order__gt=self.order).order_by('order')[0]
        except IndexError:
            return None

    def get_prev(self):
        """ get the previous Idea by order column or return
            None if this Idea instance is the first
        """
        try:
            return Idea.objects.filter(order__lt=self.order).order_by('-order')[0]
        except IndexError:
            return None

    def save(self, *args, **kwargs):
        """ if order field is None, add value
        """
        if not self.order:
            idea_idx = Idea.objects.all().aggregate(Max('order'))['order__max']
            if idea_idx:
                idea_idx += 1
            else:
                idea_idx = 1
            self.order = idea_idx

        # "real" save method
        super(Idea, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


###############################################################################
# Thought model
###############################################################################
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

    # non field members
    allowed_tags = [
        'a', 'abbr', 'ul', 'blockquote', 'code', 'em', 'strong', 'li', 'ol',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'p', 'br'
    ]

    def truncate(self, max_length=70, allowed_tags=None, strip=True):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        if not allowed_tags:
            allowed_tags = self.allowed_tags

        clean_str = self.content[:max_length]
        if max_length < len(self.content):
            clean_str += "..."

        clean_str = bleach.clean(
            clean_str,
            tags=allowed_tags,
            strip=strip,
            strip_comments=True,
        )

        return clean_str

    def save(self, *args, **kwargs):
        # check to see if this save means a draft is being published and
        # change date_published to now
        try:
            orig = Thought.objects.get(slug=self.slug)
            if orig.is_draft and not self.is_draft:
                self.date_published = datetime.datetime.now()
        except Thought.DoesNotExist as e:
            pass

        # "real" save method
        super(Thought, self).save(*args, **kwargs)

###############################################################################
# model helper methods
###############################################################################
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