import os
import datetime

import bleach
import PIL
from PIL import Image
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Crop

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

    icon = models.ImageField(upload_to=os.path.basename(paths.MEDIA_IMAGE_ROOT))
    icon_large = ImageSpecField(
        source='icon',
        processors=[ResizeToFill(300, 300)],
        format='png',
        options={'quality': '70'}
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

    def truncate(self, max_length=70, allowed_tags=None, strip=True):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        if not allowed_tags:
            allowed_tags = self.allowed_tags

        clean_str = bleach.clean(
            self.content[:max_length],
            tags=allowed_tags,
            strip=strip,
            strip_comments=True,
        )

        if max_length < len(self.content):
            clean_str += "..."

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

        # crop picture if necessary
        if not self.preview:
            return

        filename = os.path.join(paths.MEDIA_DIR, self.preview.name)

        image = Image.open(filename)
        image_size = image.size

        if image_size[0] >= lib.UPLOAD_IMAGE_SIZE[0] or image_size[1] >= lib.UPLOAD_IMAGE_SIZE[1]:
            cropped_image = image.crop((0, 0, lib.UPLOAD_IMAGE_SIZE[0], lib.UPLOAD_IMAGE_SIZE[1]))
        else:
            cropped_image = Image.new('RGBA', lib.UPLOAD_IMAGE_SIZE, lib.UPLOAD_IMAGE_MATTE)

            # calculate resize ratio (preserve aspect ratio)
            resize_ratio = min(lib.UPLOAD_IMAGE_SIZE[0] / image_size[0], lib.UPLOAD_IMAGE_SIZE[1] / image_size[1])
            new_image_size = (image_size[0] * resize_ratio, image_size[1] * resize_ratio)
            resized_image = image.resize(size=new_image_size, resample=PIL.Image.LANCZOS)

            cropped_image.paste(resized_image, ((image_size[0] - new_image_size[0]) / 2, (image_size[1] - new_image_size[1]) / 2))

        cropped_image.save(filename, 'PNG')