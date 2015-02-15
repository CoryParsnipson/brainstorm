import os
import datetime

from imagekit.models import ImageSpecField
from imagekit.processors import Crop

from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User

import paths
import lib


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
    icon = models.ImageField(
        upload_to=os.path.basename(paths.MEDIA_IMAGE_ROOT),
        blank=False,
        null=False,
    )
    icon_small = ImageSpecField(
        source='icon',
        processors=[Crop(
            width=lib.IDEA_PREVIEW_IMAGE_SMALL_SIZE[0],
            height=lib.IDEA_PREVIEW_IMAGE_SMALL_SIZE[1],
            anchor=(0.5, 0.5),
        )],
        format='png',
        options={'quality': '70'},
    )

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

    def truncate(self, max_length=500, allowed_tags=None, strip=True):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.description,
            max_length=max_length,
            strip=strip)

    def save(self, *args, **kwargs):
        """ if order field is None, add value (1 + maximum existing value)
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

        if self.icon:
            filename = os.path.join(paths.MEDIA_DIR, self.icon.name)
            lib.resize_image(filename, new_size=lib.IDEA_PREVIEW_IMAGE_SIZE)

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
    preview = models.ImageField(
        upload_to=os.path.basename(paths.MEDIA_IMAGE_ROOT),
        blank=True,
        null=True,
    )

    # non field members
    allowed_tags = [
        'abbr', 'ul', 'blockquote', 'code', 'em', 'strong', 'li', 'ol',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br'
    ]

    def truncate(self, max_length=250, allowed_tags=None, strip=True):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.content,
            max_length=max_length,
            allowed_tags=allowed_tags or self.allowed_tags,
            strip=strip)

    def get_preview(self):
        """ safe way to get preview url for this thought. Will return None if
            there is no preview picture. Use template tag |default_if_none:
            to handle template output of this function.
        """
        if self.preview and hasattr(self.preview, 'url'):
            return self.preview.url

    def get_next_thoughts(self, num=1, include_drafts=False, include_trash=False):
        """ get the next "num" thoughts in the same Idea and return a list
            of Thought objects. This list will be padded with None types such
            that it will be of length "num" always.
        """
        query_params = {
            'idea': self.idea,
            'is_draft': include_drafts,
            'is_trash': include_trash,
            'date_published__gt': self.date_published,
        }

        # note: assumes Thoughts are ordered chronologically. Reasonable
        # assumption; may change in the far future, don't worry about it
        thought_list = Thought.objects.filter(**query_params).order_by('date_published')[:num]

        # pull out thoughts in reverse order
        adjacent_thoughts = [t for idx, t in enumerate(thought_list)]

        # add padding
        adjacent_thoughts += [None] * (num - len(adjacent_thoughts))
        return adjacent_thoughts

    def get_prev_thoughts(self, num=1, include_drafts=False, include_trash=False):
        """ get the previous "num" thoughts in the same Idea and return a list
            of Thought objects. This list will be padded with None types such
            that it will be of length "num" always.
        """
        query_params = {
            'idea': self.idea,
            'is_draft': include_drafts,
            'is_trash': include_trash,
            'date_published__lt': self.date_published,
        }

        # note: assumes Thoughts are ordered chronologically. Reasonable
        # assumption; may change in the far future, don't worry about it
        thought_list = Thought.objects.filter(**query_params).order_by('-date_published')[:num]

        # pull out thoughts in reverse order
        adjacent_thoughts = [t for idx, t in enumerate(thought_list)]

        # add padding
        adjacent_thoughts += [None] * (num - len(adjacent_thoughts))
        return adjacent_thoughts

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

        # crop picture if necessary
        if not self.preview:
            return

        filename = os.path.join(paths.MEDIA_DIR, self.preview.name)
        lib.resize_image(filename, lib.THOUGHT_PREVIEW_IMAGE_SIZE)


###############################################################################
# Link Model
###############################################################################
class Highlight(models.Model):
    """ On the front page, there is a small section under the product showcase
        for the Highlight. This model is for that.
    """
    title = models.CharField(max_length=300, blank=False, null=False)
    description = models.TextField(max_length=1500)
    url = models.URLField(max_length=1000, blank=False, null=False)
    date_published = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(
        upload_to=os.path.basename(paths.MEDIA_IMAGE_ROOT),
        blank=True,
        null=True,
    )

    # non field members
    allowed_tags = [
        'p', 'br', 'em', 'strong', 'blockquote', 'quote', 'hr'
    ]

    def truncate(self, max_length=250, allowed_tags=None, strip=True):
        """ output a form of the description field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.description,
            max_length=max_length,
            allowed_tags=allowed_tags or self.allowed_tags,
            strip=strip)

    def save(self, *args, **kwargs):
        # "real" save method
        super(Highlight, self).save(*args, **kwargs)

        # crop picture if necessary
        if self.icon:
            filename = os.path.join(paths.MEDIA_DIR, self.icon.name)
            lib.resize_image(filename, lib.HIGHLIGHT_PREVIEW_IMAGE_SIZE)