import os
import json
import datetime
import urllib

import pytz
from imagekit.models import ImageSpecField
from imagekit.processors import Crop
from BeautifulSoup import BeautifulSoup

from django.db import models
from django.db.models import Max
from django.db.models.query import QuerySet
from django.conf import settings
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
        upload_to=paths.MEDIA_IMAGE_DIR,
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

    # non field members
    allowed_tags = [
        'abbr', 'ul', 'code', 'em', 'strong', 'li', 'ol', 'p',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br'
    ]

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

    def strip_tags(self):
        """ strip all html tags from content field and return the content field
        """
        return lib.strip_tags(self.description)

    def truncate(self, max_length=270, allowed_tags=None, full_link=None):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.description,
            allowed_tags=allowed_tags or self.allowed_tags,
            max_length=max_length,
            full_link=full_link,
        )

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
            lib.resize_image(self.icon.name, new_size=lib.IDEA_PREVIEW_IMAGE_SIZE)

    def delete(self, *args, **kwargs):
        lib.delete_file(self.icon.name)
        super(Idea, self).delete(*args, **kwargs)

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
    content = models.TextField(blank=True, null=True)
    idea = models.ForeignKey(Idea)
    author = models.ForeignKey(User)
    is_draft = models.BooleanField(default=True)
    is_trash = models.BooleanField(default=False)
    date_published = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    preview = models.ImageField(
        upload_to=paths.MEDIA_IMAGE_DIR,
        blank=True,
        null=True,
    )

    # non field members
    allowed_tags = [
        'abbr', 'ul', 'code', 'em', 'strong', 'li', 'ol', 'p',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br'
    ]

    def strip_tags(self):
        """ strip all html tags from content field and return the content field
        """
        return lib.strip_tags(self.content)

    def truncate(self, max_length=250, allowed_tags=None, full_link=None):
        """ output a form of the content field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.content,
            max_length=max_length,
            allowed_tags=allowed_tags or self.allowed_tags,
            full_link=full_link,
        )

    def get_preview(self):
        """ safe way to get preview url for this thought. Will return None if
            there is no preview picture. Use template tag |default_if_none:
            to handle template output of this function.
        """
        if self.preview and hasattr(self.preview, 'url'):
            return self.preview.url
        return self.idea.icon.url

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

    def is_edited(self, delta=datetime.timedelta(minutes=1)):
        """ compare date_published and date_edited with margin of error and
            return a boolean (True if date_published != date_edited and
            False if date_published == date_edited, within margin of error)
        """
        if self.date_edited - self.date_published < delta:
            return False
        return True

    def get_image_urls(self):
        """ parse the html in the content field and return a list of
            image urls (relative to media url) for processing
        """
        soup = BeautifulSoup(self.content)
        return [image['src'] for image in soup.findAll('img')]

    def display_compact_date(self):
        return lib.display_compact_date(self.date_published)

    def save(self, *args, **kwargs):
        # check to see if this save means a draft is being published and
        # change date_published to now
        auto_update = kwargs['auto_update'] if 'auto_update' in kwargs else True
        try:
            if auto_update:
                orig = Thought.objects.get(slug=self.slug)
                if orig.is_draft and not self.is_draft:
                    self.date_published = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.now())
        except Thought.DoesNotExist:
            pass

        # "real" save method
        super(Thought, self).save()

        # crop picture if necessary
        if not self.preview:
            return

        lib.resize_image(self.preview.name, lib.THOUGHT_PREVIEW_IMAGE_SIZE)

    def delete(self, *args, **kwargs):
        lib.delete_file(self.preview.name)

        # remove inline images
        for image in self.get_image_urls():
            image = os.path.basename(image)
            image = os.path.join(paths.MEDIA_IMAGE_DIR, image)
            lib.delete_file(image)

        super(Thought, self).delete(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '"' + self.title + '"' + " (" + self.slug + ")"


###############################################################################
# Highlight Model
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
        upload_to=paths.MEDIA_IMAGE_DIR,
        blank=True,
        null=True,
    )

    # non field members
    allowed_tags = [
        'br', 'em', 'strong', 'blockquote', 'quote', 'hr', 'p'
    ]

    def strip_tags(self):
        """ strip all html tags from content field and return the content field
        """
        return lib.strip_tags(self.description)

    def truncate(self, max_length=250, allowed_tags=None, full_link=None):
        """ output a form of the description field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.description,
            max_length=max_length,
            allowed_tags=allowed_tags or self.allowed_tags,
            full_link=full_link,
        )

    def display_compact_date(self):
        return lib.display_compact_date(self.date_published)

    def save(self, *args, **kwargs):
        # "real" save method
        super(Highlight, self).save(*args, **kwargs)

        # crop picture if necessary
        if self.icon:
            lib.resize_image(self.icon.name, lib.HIGHLIGHT_PREVIEW_IMAGE_SIZE)

    def delete(self, *args, **kwargs):
        lib.delete_file(self.icon.name)
        super(Highlight, self).delete(*args, **kwargs)


###############################################################################
# Reading List
###############################################################################
class ReadingListItem(models.Model):
    """ Recently read books list, favorite books, etc. Woohoo
    """
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150)
    link = models.URLField(max_length=400)
    description = models.CharField(max_length=200, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True)
    wishlist = models.BooleanField(default=False)
    favorite = models.BooleanField(default=False)
    cover = models.URLField(max_length=400)

    def strip_tags(self):
        """ strip all html tags from content field and return the content field
        """
        return lib.strip_tags(self.description)

    def display_compact_date(self):
        return lib.display_compact_date(self.date_published)

    def save(self, *args, **kwargs):
        if self.date_published:
            self.date_published = datetime.datetime.now()

        # "real" save method
        super(ReadingListItem, self).save(*args, **kwargs)


###############################################################################
# Task (To Do list items)
###############################################################################
class Task(models.Model):
    """ To do list that you see in the dashboard. This shouldn't be public.
        Tasks can be marked completed. Tasks can also have subtasks (they can
        be decomposed into smaller chunks). When a Task has subtasks, they can
        only be marked completed when all subtasks are completed.
    """
    PRIORITY = (
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High'),
        (3, 'Next'),
    )

    parent_task = models.ForeignKey('Task', blank=True, null=True)
    idea = models.ForeignKey(Idea, blank=True, null=True)
    content = models.CharField(max_length=300)
    date_added = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITY, default=PRIORITY[1][0], blank=True)

    @staticmethod
    def reorder_child_tasks(task_list, show_complete=False):
        """ give a Queryset (or list) of Task instances, reorder
            child tasks to come after their parent tasks. The subtasks will
            also be ordered in order of priority then date added.

            NOTE: this is not tested for task lists that have nesting of more
                  than one level
        """
        if not task_list or not isinstance(task_list, QuerySet):
            return task_list

        reordered_tasks = list(task_list.filter(parent_task__isnull=True).order_by("-priority", "-date_added"))
        for t in task_list:
            if show_complete:
                subtasks = Task.objects.filter(parent_task=t)
            else:
                subtasks = Task.objects.filter(is_completed=False, parent_task=t)
            if not subtasks:
                continue
            subtasks = subtasks.order_by("-priority", "-date_added")

            insert_idx = reordered_tasks.index(t)
            reordered_tasks = reordered_tasks[:insert_idx + 1] + list(subtasks) + reordered_tasks[insert_idx + 1:]

        return reordered_tasks

    def has_subtasks(self):
        """ check to see if this task has subtasks. NOTE: this function will
            return fals if this task has subtasks, but they are all complete
        """
        return Task.objects.filter(is_completed=False, parent_task=self).count() > 0

    def display_date_added(self):
        return lib.display_compact_date(self.date_added)

    def display_date_completed(self):
        return lib.display_compact_date(self.date_completed)

    def save(self):
        try:
            orig = Task.objects.get(id=self.id)
            if not orig.is_completed and self.is_completed:
                # set completed date if is_completed is marked True
                self.date_completed = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.now())

                # set priority to low
                self.priority = self.PRIORITY[0][0]
        except Task.DoesNotExist:
            pass

        # "real" save method
        super(Task, self).save()

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        content = lib.strip_tags(lib.truncate(content=self.content, max_length=50, allowed_tags=[]))
        return "Task #%d: %s" % (self.id, content)


###############################################################################
# Note (unfinished thoughts that aren't associated with a specific Thought yet)
###############################################################################
class Note(models.Model):
    """ written notes for things to research or write about. These also
        shouldn't be public. The idea is to write down information that
        isn't coherent enough for a thought, but are good seeds for
        later. Notes should be able to be linked to ideas, but it is
        not necessary, as they shouldn't represent fully formed thoughts.
    """
    ideas = models.ManyToManyField(Idea, blank=True)
    thoughts = models.ManyToManyField(Thought, blank=True)
    title = models.CharField(max_length=75)
    content = models.TextField(max_length=5000)
    date_published = models.DateTimeField(auto_now_add=True)

    # non field members
    allowed_tags = [
        'br', 'em', 'strong', 'blockquote', 'quote', 'hr', 'ul', 'li', 'ol', 'p'
    ]

    def add_idea(self, idea_slug):
        """ add an idea instance to list of associated Ideas. Note: duplicate
            ideas will not be added; ValueError exception will be raised
        """
        try:
            idea_slug = lib.slugify(idea_slug)
            idea = Idea.objects.filter(slug=idea_slug)
        except Idea.DoesNotExist:
            raise ValueError("Idea '%s' does not exist." % idea_slug)

        if self.ideas.filter(slug=idea.slug).exists():
            raise ValueError("Idea '%s' is already associated with Note '%s'" % (idea_slug, self.title))

        self.ideas.add(idea)

    def add_thought(self, thought_slug):
        """ add a thought instance to list of associated Thoughts. Note:
            duplicate thoughts will not be added: ValueError exception
            will be raised
        """
        try:
            thought_slug = lib.slugify(thought_slug)
            thought = Thought.objects.filter(slug=thought_slug)
        except Thought.DoesNotExist:
            raise ValueError("Thought '%s' does not exist." % thought_slug)

        if self.thoughts.filter(slug=thought.slug).exists():
            raise ValueError("Thought '%s' is already associated with Note '%s'" % (thought_slug, self.title))

        self.thoughts.add(thought)

    def strip_tags(self):
        """ return content field with no html tags included
        """
        return lib.strip_tags(self.content)

    def truncate(self, max_length=150, allowed_tags=None, full_link=None):
        """ output a form of the description field, truncated to max_length. Tags
            will be whitelisted, stripped, and balanced to account for
            truncation.
        """
        return lib.truncate(
            content=self.content,
            max_length=max_length,
            allowed_tags=allowed_tags or self.allowed_tags,
            full_link=full_link,
        )

    def display_fancy_date(self):
        return lib.display_fancy_date(self.date_published)

    def display_compact_date(self):
        return lib.display_compact_date(self.date_published)


###############################################################################
# Activity (activity feed item)
###############################################################################
class Activity(models.Model):
    """ this item records a singular action done by an admin user on the site.
        Examples of this include when a user posts a new new thought, adds
        a book to the reading list, or marks a task complete.
    """
    TYPE = (
        (0, 'Create Idea'),
        (1, 'Edited Idea'),
        (2, 'Deleted Idea'),
        (3, 'Started Draft'),
        (4, 'Published Draft'),
        (5, 'Edited Draft'),
        (6, 'Moved Draft'),
        (7, 'Trashed Draft'),
        (8, 'Untrashed Draft'),
        (9, 'Deleted Draft'),
        (10, 'Published Thought'),
        (11, 'Unpublished Thought'),
        (12, 'Edited Thought'),
        (13, 'Moved Thought'),
        (14, 'Trashed Thought'),
        (15, 'Untrashed Thought'),
        (16, 'Deleted Thought'),
        (17, 'Added New Highlight'),
        (18, 'Edited Highlight'),
        (19, 'Deleted Highlight'),
        (20, 'Added Book to Recently Read List'),
        (21, 'Added Book to Wish List'),
        (22, 'Edited Book'),
        (23, 'Moved Book to Recently Read List'),
        (24, 'Deleted Book'),
        (25, 'Added New Task Item'),
        (26, 'Edited Task Item'),
        (27, 'Deleted Task Item'),
        (28, 'Marked Task Item as Completed'),
        (29, 'Changed Task Priority'),
        (30, 'Started New Note'),
        (31, 'Edited Note'),
        (32, 'Deleted Note'),
        (33, 'Tweet'),
    )

    author = models.ForeignKey(User)
    type = models.IntegerField(choices=TYPE, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    tokens = models.CharField(max_length=2000, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)

    @staticmethod
    def get_type_id(type_string):
        return list(Activity.TYPE)[[v for (k, v) in Activity.TYPE].index(type_string)][0]

    def store_tokens(self, token_dict={}):
        """ serialize token dict to a JSON string and then store it in the tokens CharField
        """
        if not token_dict:
            return
        self.tokens = json.dumps(token_dict)

    def get_tokens(self):
        """ unserialize token dict stored in model instance data. Will return
            an empty dictionary if there is no token data
        """
        if not self.tokens:
            return {}
        return json.loads(self.tokens)

    def generate_message(self):
        """ generate output string for this Activity item. Uses information
            from type field as well as any optional data stored in the
            tokens field.
        """
        if Activity.TYPE[int(self.type)][1] == 'Create Idea':
            msg = "created a new <span class='excerpt'>Idea</span> <span class='idea'>%s</span>" % self.get_tokens()['name']
        elif Activity.TYPE[int(self.type)][1] == 'Edited Idea':
            msg = "edited <span class='excerpt'>Idea</span> <span class='idea'>%s</span>" % self.get_tokens()['name']
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Idea':
            msg = "deleted <span class='excerpt'>Idea</span> <span class='idea'>%s</span>" % self.get_tokens()['name']
        elif Activity.TYPE[int(self.type)][1] == 'Started Draft':
            msg = "started a new <span class='excerpt'>Draft</span> titled <span class='draft'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Published Draft':
            # took draft(s) that were already saved and published it/them
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "published %d <span class='draft'>Drafts</span>" % int(t['length'])
            else:
                msg = "published <span class='excerpt'>Draft</span> <span class='draft'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Edited Draft':
            msg = "edited <span class='excerpt'>Draft</span> <span class='draft'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Moved Draft':
            t = self.get_tokens()
            msg = "moved <span class='excerpt'>Draft</span> <span class='draft'>%s</span> from <span class='excerpt'>Idea</span> <span class='idea'>%s</span> to <span class='idea'>%s</span>"\
                  % (t['title'], t['old_idea'], t['new_idea'])
        elif Activity.TYPE[int(self.type)][1] == 'Trashed Draft':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "moved %d <span class='draft'>Drafts</span> to the trash" % int(t['length'])
            else:
                msg = "moved <span class='excerpt'>Draft</span> <span class='draft'>%s</span> to the trash" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Untrashed Draft':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "untrashed %d <span class='draft'>Drafts</span>" % int(t['length'])
            else:
                msg = "untrashed <span class='excerpt'>Draft</span> <span class='draft'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Draft':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "deleted %d <span class='draft'>Drafts</span>" % int(t['length'])
            else:
                msg = "deleted <span class='excerpt'>Draft</span> <span class='draft'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Published Thought':
            # created a thought and published it without saving as a draft
            msg = "published a new <span class='excerpt'>Thought</span> <span class='thought'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Unpublished Thought':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "unpublished %d <span class='thought'>Thoughts</span>" % int(t['length'])
            else:
                msg = "unpublished <span class='excerpt'>Thought</span> <span class='thought'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Edited Thought':
            msg = "edited <span class='excerpt'>Thought</span> <span class='thought'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Moved Thought':
            t = self.get_tokens()
            msg = "moved <span class='excerpt'>Thought</span> <span class='thought'>%s</span> from <span class='excerpt'>Idea</span> <span class='idea'>%s</span> to <span class='idea'>%s</span>"\
                  % (t['title'], t['old_idea'], t['new_idea'])
        elif Activity.TYPE[int(self.type)][1] == 'Trashed Thought':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "moved %d <span class='thought'>Thoughts</span> to the trash" % int(t['length'])
            else:
                msg = "moved <span class='excerpt'>Thought</span> <span class='thought'>%s</span> to the trash" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Untrashed Thought':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "untrashed %d <span class='thought'>Thoughts</span>" % int(t['length'])
            else:
                msg = "untrashed <span class='excerpt'>Thought</span> <span class='thought'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Thought':
            t = self.get_tokens()
            if int(t['length']) > 1:
                msg = "deleted %d <span class='thought'>Thoughts</span> from trash" % int(t['length'])
            else:
                msg = "deleted <span class='excerpt'>Thought</span> <span class='thought'>%s</span> from trash" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Added New Highlight':
            msg = "added new <span class='excerpt'>Highlight</span> <span class='highlight'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Edited Highlight':
            msg = "edited <span class='excerpt'>Highlight</span> <span class='highlight'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Highlight':
            msg = "deleted <span class='excerpt'>Highlight</span> <span class='highlight'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Added Book to Recently Read List':
            msg = "added <span class='book'>%s</span> to the recently read list" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Added Book to Wish List':
            msg = "added <span class='book'>%s</span> to the wish list" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Edited Book':
            msg = "edited <span class='excerpt'>Reading List Book</span> <span class='book'>%s</span>" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Moved Book to Recently Read List':
            msg = "Moved <span class='book'>%s</span> from wish list to recently read list" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Book':
            msg = "deleted <span class='book'>%s</span> from the reading list" % self.get_tokens()['title']
        elif Activity.TYPE[int(self.type)][1] == 'Added New Task Item':
            t = self.get_tokens()
            msg = "added new <span class='excerpt'>Task #%d:</span> <span class='task'>%s</span>" % (t['id'], t['content'])
        elif Activity.TYPE[int(self.type)][1] == 'Edited Task Item':
            t = self.get_tokens()
            msg = "edited <span class='excerpt'>Task #%d:</span> <span class='task'>%s</span>" % (t['id'], t['content'])
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Task Item':
            t = self.get_tokens()
            msg = "deleted <span class='excerpt'>Task #%d:</span> <span class='task'>%s</span>" % (t['id'], t['content'])
        elif Activity.TYPE[int(self.type)][1] == 'Marked Task Item as Completed':
            t = self.get_tokens()
            msg = "marked <span class='excerpt'>Task #%d:</span> <span class='task'>%s</span> as completed" % (t['id'], t['content'])
        elif Activity.TYPE[int(self.type)][1] == 'Changed Task Priority':
            t = self.get_tokens()
            msg = "changed priority of <span class='excerpt'>Task #%d:</span> <span class='task'>%s</span> from <span class='excerpt'>%s</span> to <span class='excerpt'>%s</span>" %\
                  (t['id'], t['content'], Task.PRIORITY[t['old_priority']][1], Task.PRIORITY[t['new_priority']][1])
        elif Activity.TYPE[int(self.type)][1] == 'Started New Note':
            t = self.get_tokens()
            msg = "started new <span class='excerpt'>Note #%d:</span> <span class='note'>%s</span>" % (t['id'], t['title'])
        elif Activity.TYPE[int(self.type)][1] == 'Edited Note':
            t = self.get_tokens()
            msg = "edited <span class='excerpt'>Note #%d:</span> <span class='note'>%s</span>" % (t['id'], t['title'])
        elif Activity.TYPE[int(self.type)][1] == 'Deleted Note':
            t = self.get_tokens()
            msg = "deleted <span class='excerpt'>Note #%d:</span> <span class='note'>%s</span>" % (t['id'], t['title'])
        #elif Activity.TYPE[int(self.type)][1] == 'Tweet':
        else:
            raise IndexError("Invalid Activity Type")

        return msg

    def display_date(self):
        return lib.display_fancy_date(self.date)
