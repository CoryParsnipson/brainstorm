import os
import re
import io
import datetime

import requests
import boto
import pytz
import PIL
from PIL import Image
from lxml import etree
from lxml.html.clean import Cleaner

from django.conf import settings
from django.contrib import messages
from django.template import defaultfilters
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.http import urlunquote_plus

import paths
import common

###############################################################################
# app level defines
###############################################################################
MAX_UPLOAD_SIZE = 104857600  # (1024 * 1024 bits * 100)

THOUGHT_PREVIEW_IMAGE_SIZE = (600, 300)
IDEA_PREVIEW_IMAGE_SMALL_SIZE = (600, 150)
IDEA_PREVIEW_IMAGE_SIZE = (600, 300)
HIGHLIGHT_PREVIEW_IMAGE_SIZE = (200, 150)

DEFAULT_TRUNCATE_LENGTH = 70
ALLOWED_TAGS = [
    'abbr', 'ul', 'blockquote', 'code', 'em', 'strong', 'li', 'ol',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br'
]

PAGINATION_FRONT_PER_PAGE = 8 
PAGINATION_IDEAS_PER_PAGE = 5
PAGINATION_THOUGHTS_PER_PAGE = 10
PAGINATION_READINGLIST_PER_PAGE = 20
PAGINATION_HIGHLIGHTS_PER_PAGE = 10
PAGINATION_DASHBOARD_ACTIVITY_PER_PAGE = 30
PAGINATION_DASHBOARD_READINGLIST_PER_PAGE = 15
PAGINATION_DASHBOARD_HIGHLIGHTS_PER_PAGE = 30
PAGINATION_DASHBOARD_NOTES_PER_PAGE = 30
PAGINATION_DASHBOARD_TASKS_PER_PAGE = 30
PAGINATION_DASHBOARD_IDEAS_PER_PAGE = 10
PAGINATION_DASHBOARD_THOUGHTS_PER_PAGE = 50
PAGINATION_DASHBOARD_DRAFTS_PER_PAGE = 50
PAGINATION_DASHBOARD_TRASH_PER_PAGE = 50

PAGINATION_FRONT_PAGES_TO_LEAD = 0
PAGINATION_IDEAS_PAGES_TO_LEAD = 2
PAGINATION_THOUGHTS_PAGES_TO_LEAD = 2
PAGINATION_READINGLIST_PAGES_TO_LEAD = 3
PAGINATION_HIGHLIGHTS_PAGES_TO_LEAD = 3
PAGINATION_DASHBOARD_ACTIVITY_PAGES_TO_LEAD = 0
PAGINATION_DASHBOARD_READINGLIST_PAGES_TO_LEAD = 2
PAGINATION_DASHBOARD_HIGHLIGHTS_PAGES_TO_LEAD = 2 
PAGINATION_DASHBOARD_NOTES_PAGES_TO_LEAD = 0
PAGINATION_DASHBOARD_TASKS_PAGES_TO_LEAD = 2
PAGINATION_DASHBOARD_IDEAS_PAGES_TO_LEAD = 2
PAGINATION_DASHBOARD_THOUGHTS_PAGES_TO_LEAD = 2
PAGINATION_DASHBOARD_DRAFTS_PAGES_TO_LEAD = 2
PAGINATION_DASHBOARD_TRASH_PAGES_TO_LEAD = 2

NUM_RECENT_IDEAS = 3

NUM_IDEAS_FOOTER = 3

MAX_NUM_BOOK_RESULTS = 5
NUM_READ_LIST = 3
NUM_TASK_LIST = 3
NUM_NOTE_LIST = 5


###############################################################################
# classes
###############################################################################
class BookSearch:
    google_book_api_get_string = "https://www.googleapis.com/books/v1/volumes?q="

    def search(self, keywords, max_len=MAX_NUM_BOOK_RESULTS):
        """ given a string containing keywords, make a call to an external
            API and return a list of results

            Each result is a dictionary with the following keys:
              'url' => url to book page
              'title' => title of book
              'author' => author of the book
              'cover' => thumbnail url of image
        """
        if not keywords:
            return []

        # this implementation uses public google books api
        query = self.google_book_api_get_string + keywords
        http_resp = requests.get(query)

        books = []
        book_idx = 0
        for book in http_resp.json()["items"]:
            if book_idx >= max_len:
                break

            book_idx += 1

            try:
                books.append({
                    'url' : book["volumeInfo"]["infoLink"],
                    'cover' : book["volumeInfo"]["imageLinks"]["smallThumbnail"],
                    'title' : book["volumeInfo"]["title"],
                    'author' : book["volumeInfo"]["authors"][0],
                })
            except KeyError:
                book_idx -= 1

        return books

class FlashMessageManager:
    def __init__(self):
        self.cached_messages = []

    def hash_message(self, msg_data):
        """ take the first two entries in the msg_data tuple and calculate python hash() of it.
        """
        return hash((msg_data['action'], msg_data['status']))

    def add_message(self, raw_msg_data):
        """ add a message to the cached message list. It will hash the first two entries (msg action
            string and msg status bool) to fold duplicates together and combine the tokens
        """
        was_folded = False
        for c_msg in self.cached_messages:
            if not self.hash_message(raw_msg_data) == self.hash_message(c_msg):
                continue

            # update cached message entry
            c_msg['tokens'].append(raw_msg_data['tokens'])

            was_folded = True
            break

        if not was_folded:
            # add message to the queue
            self.cached_messages.append({
                'action': raw_msg_data['action'],
                'status': raw_msg_data['status'],
                'tokens': [raw_msg_data['tokens']],  # convert raw_msg_data tokens dict into list of dicts
                'extra_html': raw_msg_data['extra_html'],
            })

    def format_message(self, msg_data):
        """ take the tuple items and format a message string from the contents
        """
        if msg_data['action'] == 'idea_delete':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Successfully deleted %d Ideas." % len(msg_data['tokens'])
                else:
                    msg = "Successfully deleted Idea '%s'." % msg_data['tokens'][0]['idea']
            else:
                msg = msg_data['action'] + ': %s.' % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'idea_order_up' or msg_data['action'] == 'idea_order_down':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "%d Ideas were moved %s." % (
                        len(msg_data['tokens']),
                        'up' if msg_data['action'] == 'idea_order_up' else 'down',
                    )
                else:
                    msg = "Idea %s was moved %s." % (
                        msg_data['tokens'][0]['idea'],
                        'up' if msg_data['action'] == 'idea_order_up' else 'down',
                    )
            else:
                msg = msg_data['action'] + ': %s.' % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'thought_trash' or msg_data['action'] == 'thought_untrash':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "%d Thoughts were %strashed." % (
                        len(msg_data['tokens']),
                        '' if msg_data['action'] == 'thought_trash' else 'un',
                    )
                else:
                    msg = "Thought '%s' was %strashed." % (
                        msg_data['tokens'][0]['thought'],
                        '' if msg_data['action'] == 'thought_trash' else 'un',
                    )
            else:
                msg = msg_data['action'] + ': %s.' % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'thought_publish' or msg_data['action'] == 'thought_unpublish':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Moved %d Thoughts to '%s'." % (len(msg_data['tokens']), msg_data['tokens'][0]['page'])
                else:
                    msg = "Moved Thought '%s' to %s." % (msg_data['tokens'][0]['thought'], msg_data['tokens'][0]['page'])
            else:
                msg = msg_data['action'] + ': %s.' % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'thought_idea_move':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Moved %d Thoughts to Idea '%s'." % (len(msg_data['tokens']), msg_data['tokens'][0]['idea'])
                else:
                    msg = "Moved Thought '%s' to Idea '%s'." % (msg_data['tokens'][0]['thought'], msg_data['tokens'][0]['idea'])
            else:
                msg = msg_data['action'] + ": %s." % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'thought_delete':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Successfully deleted %d Thoughts." % len(msg_data['tokens'])
                else:
                    msg = "Successfully deleted Thought '%s'." % msg_data['tokens'][0]['thought']
            else:
                msg = msg_data['action'] + ": %s." % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'highlight_delete':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Successfully deleted %d Highlights." % len(msg_data['tokens'])
                else:
                    msg = "Successfully deleted Highlight '%s' (#%d)." % \
                          (msg_data['tokens'][0]['highlight_title'], msg_data['tokens'][0]['highlight_id'])
            else:
                msg = msg_data['action'] + " (#%d): %s." % \
                    (msg_data['tokens'][0]['highlight'], msg_data['tokens'][0]['error'])
        elif msg_data['action'] == 'book_delete':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Successfully deleted %d Books." % len(msg_data['tokens'])
                else:
                    msg = "Successfully deleted Book '%s'." % msg_data['tokens'][0]['book_title']
            else:
                msg = msg_data['action'] + ": %s." % msg_data['tokens'][0]['error']
        elif msg_data['action'] == 'note_delete':
            if msg_data['status']:
                if len(msg_data['tokens']) > 1:
                    msg = "Successfully deleted %d Notes." % len(msg_data['tokens'])
                else:
                    msg = "Successfully deleted Note '%s'." % msg_data['tokens'][0]['title']
            else:
                msg = msg_data['action'] + ": %s." % msg_data['tokens'][0]['error']
        else:
            return "Unknown Message: '%s', tokens: '%s'." % (msg_data['action'], msg_data['tokens'].__str__())

        return "<p>" + msg + "</p>" + msg_data['extra_html']

    def flush_messages_to_user(self, request):
        """ take all messages in cached message and display them to the user
            (using the django message framework)
        """
        for msg in self.cached_messages:
            messages.add_message(
                request,
                messages.SUCCESS if msg['status'] else messages.ERROR,
                self.format_message(msg)
            )


###############################################################################
# methods and code common to entire blog app
###############################################################################
def remove_duplicates(seq):
    """ remove duplicates from a python list; from
        stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def replace_tokens(search_string, token_vals):
    """ given a string with tokens, a token regular expression, and a dictionary of token values
        search for tokens in the string and replace them from the dictionary

        Note: token format is {token}
        Note: token_vals should be a dictionary where keys are all values found in place of "token"
              from token format
    """
    missing_keys = True
    search_string = urlunquote_plus(search_string)
    final_string = search_string

    while missing_keys:
        try:
            final_string = search_string.format(**token_vals)
            missing_keys = False
        except KeyError as e:
            # if we find a missing token, do not replace it
            token_vals[e.message] = '{' + e.message + '}'

    return final_string


def slugify(source_str, max_len=30):
    """ create a nice slug given a string; FYI, Django comes with a prebuilt
        slugify function (django.template.defaultfilters) which handles
        non-unicode characters too, but doesn't truncate.

    :param source_str: string to make slug out of
    :param max_len: maximum length of slug
    :return: a string that is a valid slug
    """
    # remove non alphanumeric characters
    urlenc_regex = re.compile(r'[^A-Za-z0-9\-_]+')
    source_str = urlenc_regex.sub(' ', source_str)

    # collapse all spaces
    space_collapse_regex = re.compile(r'\s+')
    source_str = space_collapse_regex.sub(' ', source_str)

    # strip trailing/leading spaces, convert to lowercase, and split into words
    str_words = source_str.strip().lower().split(' ')

    counted_len = len(str_words[0]) + 1
    slug_tokens = [str_words.pop(0)]
    while str_words and counted_len + len(str_words[0]) <= max_len:
        counted_len += len(str_words[0]) + 1
        slug_tokens.append(str_words.pop(0))

    slug = "-".join(slug_tokens)
    return slug


def truncate(content, max_length=DEFAULT_TRUNCATE_LENGTH, allowed_tags=ALLOWED_TAGS, full_link=None):
    """ truncate a body of text to the expected 'max_length' and strip
        the body of text of all html tags that are not in 'allowed tags'. You
        can also specify a 'strip' value (True -> strip html tags, False ->
        escape html tags and leave them in text)
    """
    if not content:
        return ''

    cleaner = Cleaner(
        page_structure=False,
        links=True,
        safe_attrs_only=True,
        remove_unknown_tags=False,
        allow_tags=allowed_tags
    )

    content = defaultfilters.truncatechars_html(cleaner.clean_html(content), max_length)
    if full_link:
        try:
            insert_point = content.rindex('</p>')
        except ValueError:
            insert_point = content.rindex('<')

        ending = content[insert_point:]
        content = content[:insert_point]

        content += '&nbsp;<a href="' + full_link + '">(Read More)</a>' + ending
    return content


def generate_upload_filename(filename, full_path=None):
    """ given a string (presumably an original filename with extension),
        generate a non-conflicting filename for user uploads
    """
    filename = os.path.basename(filename)
    basename, ext = os.path.splitext(filename)

    if ext.lower() in ['.bmp', '.png', '.gif', '.jpg', '.jpeg', '.tiff']:
        file_dir = paths.MEDIA_IMAGE_DIR
    elif ext.lower() in ['.mp4', '.mpg', '.avi', '.xvid', '.divx', '.ogm']:
        file_dir = paths.MEDIA_VIDEO_DIR
    else:
        file_dir = paths.MEDIA_FILE_DIR

    # check for existence
    file_idx = 1
    name = basename
    while default_storage.exists(os.path.join(file_dir, name + ext)):
        name = basename + "-" + str(file_idx)
        file_idx += 1

    if full_path:
        file_url = os.path.normpath(os.path.join(file_dir, name + ext))
        file_url = os.path.join(settings.MEDIA_URL, file_url)
        return file_url
    return name + ext


def upload_file(f):
    """ Given file post data, place filedata into media directory

        Watch out. This function will return True, file_url if the
        file already exists. This will point to the right url, but
        maybe not be the file you were expecting.

        Returns 2-tuple (Boolean, String)
          success -> True, file_url of newly created file
          failure -> False, error message
    """
    # determine correct folder depending on content_type
    content_category = f.content_type.split("/")[0]
    if content_category == "image":
        file_dir = paths.MEDIA_IMAGE_DIR
    elif content_category == "video":
        file_dir = paths.MEDIA_VIDEO_DIR
    else:
        file_dir = paths.MEDIA_FILE_DIR

    file_url = os.path.join(file_dir, generate_upload_filename(f.name))

    # enforce file size limit
    if f.size > MAX_UPLOAD_SIZE:
        return False, "%s exceeds maximum upload size!" % f.name

    try:
        uploaded_file = default_storage.open(file_url, 'wb')
        uploaded_file.write(f.read())
        uploaded_file.close()

        # if we are on Amazon S3, preserve the content type
        if os.environ['DJANGO_SETTINGS_MODULE'].endswith('production'):
            boto_url = os.path.join(paths.MEDIA_DIR, file_url)
            key = boto.connect_s3().get_bucket(os.environ['S3_BUCKET_NAME']).lookup(boto_url)
            key.copy(key.bucket, key.name, preserve_acl=True,
                     metadata={'Content-Type': f.content_type})
    except Exception as e:
        return False, e.message

    return True, file_url


def delete_file(filename):
    """ given a url (relative to the media url), delete the file
        from the server.
    """
    if filename and default_storage.exists(filename):
        default_storage.delete(filename)


def get_center_coord(box, rect):
    """ given a tuple (x, y) "box" representing a rectangle where x is the
        width of the rectangle in pixels and y is the height, and another
        tuple "rect", return a coordinate pair (x_offset, y_offset) such that
        box will be centered inside rect.
    """
    return (max(0, int(float(rect[0] - box[0]) / 2)),
            max(0, int(float(rect[1] - box[1]) / 2)))


def resize_image(filename, new_size=THOUGHT_PREVIEW_IMAGE_SIZE):
    """ Given a filename to an existing image file, resize the
        file to the given dimensions (new_size). If no dimensions
        are provided, the file will be resized and cropped to the
        value in THOUGHT_PREVIEW_IMAGE_SIZE. The new image will
        be saved over the existing filename.
    """
    # retrieve file
    fp = io.BytesIO(default_storage.open(filename).read())
    image = Image.open(fp)
    image_size = image.size

    if image_size[0] < new_size[0] or image_size[1] < new_size[1]:
        # find the smallest dimension, upscale, and crop
        resize_ratio = max(float(new_size[0]) / image_size[0],
                           float(new_size[1]) / image_size[1])
        image_size = (int(image_size[0] * resize_ratio),
                      int(image_size[1] * resize_ratio))
        image = image.resize(size=image_size, resample=PIL.Image.LANCZOS)
    elif image_size[0] > new_size[0] or image_size[1] > new_size[1]:
        # if the image is larger, find smallest edge, and shrink
        resize_ratio = max(float(new_size[0]) / image_size[0],
                           float(new_size[1]) / image_size[1])
        image_size = (int(image_size[0] * resize_ratio),
                      int(image_size[1] * resize_ratio))
        image = image.resize(size=image_size, resample=PIL.Image.LANCZOS)
    else:
        # image is already the perfect size, don't resize
        return

    (offset_x, offset_y) = get_center_coord(new_size, image_size)
    crop_box = (offset_x, offset_y, offset_x + new_size[0], offset_y + new_size[1])

    cropped_image = image.crop(crop_box)

    # save file back to same url
    out_img = io.BytesIO()
    cropped_image.save(out_img, 'PNG')
    image_file = default_storage.open(filename, 'wb')
    image_file.write(out_img.getvalue())
    image_file.close()

    # instead of the Amazon S3 stanza, give this a try:
    # if hasattr(image_file, "_storage"):
    #   image_file._storage.headers['Content-Type'] = ''

    # if we are on Amazon S3, set the content type
    if os.environ['DJANGO_SETTINGS_MODULE'].endswith('production'):
        boto_url = os.path.join(paths.MEDIA_DIR, filename)
        key = boto.connect_s3().get_bucket(os.environ['S3_BUCKET_NAME']).lookup(boto_url)
        key.copy(key.bucket, key.name, preserve_acl=True,
                 metadata={'Content-Type': 'image/png'})


def create_pagination(queryset, current_page, per_page=PAGINATION_THOUGHTS_PER_PAGE, page_lead=PAGINATION_THOUGHTS_PAGES_TO_LEAD):
    """ given a queryset or list, return a dict of items to construct a
        paginated list in template

        The dict is as follows:
        {
          'first': [page number]
          'last': [page number]
          'next': [page number]
          'prev': [page number]
          'pages': [list of page numbers] (may contain 'None' for '...')
        }
    """
    paginator = Paginator(queryset, per_page)
    pagination = {
        'first': 1,
        'last': paginator.num_pages,
        'pages': [],
    }

    try:
        current_page = paginator.page(current_page)
    except (EmptyPage, PageNotAnInteger):
        current_page = paginator.page(1)

    pagination['current'] = current_page.number

    try:
        pagination['next'] = current_page.next_page_number()
    except EmptyPage:
        # current page is last page
        pagination['next'] = None

    try:
        pagination['prev'] = current_page.previous_page_number()
    except EmptyPage:
        # current page is first page
        pagination['prev'] = None

    if page_lead > 0:
        lower_pages = range(max(current_page.number - page_lead, 1), current_page.number)
        upper_pages = range(current_page.number + 1, min(current_page.number + page_lead + 1, paginator.num_pages + 1))
    else:
        lower_pages = []
        upper_pages = []

    pagination['pages'] = lower_pages + [current_page.number] + upper_pages

    return pagination


def create_paginator(queryset, per_page, page=1):
    """ given a queryset and two parameters (PAGINATION_<list>_PER_PAGE and
        PAGINATION_<list>_PAGES_TO_LEAD), create a paginator object and
        return it
    """
    paginator = Paginator(queryset, per_page)
    try:
        items_on_page = paginator.page(page)
    except PageNotAnInteger:
        items_on_page = paginator.page(1)
    except EmptyPage:
        items_on_page = paginator.page(paginator.num_pages)
    return paginator, items_on_page


def display_compact_date(dt=None):
    """ get the date for display in a compact list type setting

        For instance, it will display 'Mar 16' or '2:11 PM' depending on how
        far in the past the date is.
    """
    now = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.now())
    age = now - (dt or now)

    if age < datetime.timedelta(seconds=60):
        display_date = "Now"
    elif age < datetime.timedelta(minutes=60):
        display_date = "%s min ago" % (age.seconds / 60)
    elif age < datetime.timedelta(hours=4):
        display_date = "%s hr%s ago" % (age.seconds / 3600, 's' if age.seconds > 7200 else '')
    elif age < datetime.timedelta(days=1):
        display_date = timezone.localtime(dt).strftime("%I:%M %p").lstrip('0')
    elif age < datetime.timedelta(days=5):
        display_date = "%s day%s ago" % (age.days, 's' if age.days > 1 else '')
    else:
        display_date = dt.strftime("%b %d")

    return display_date


def display_fancy_date(dt=None):
    """ get the date for display in a nicely-human readible way

        For instance, it will display 'March 16' or '15 minutes ago' depending on the
        given datetime. For any time longer than 4 hours in the past, the function
        will return 'Today' and instead of '1 day ago', it will display 'Yesterday'.
    """
    now = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.now())
    age = now - (dt or now)

    if age < datetime.timedelta(seconds=60):
        display_date = "Now"
    elif age < datetime.timedelta(minutes=60):
        display_date = "%s minute%s ago" % (age.seconds / 60, 's' if age.seconds > 120 else '')
    elif age < datetime.timedelta(hours=4):
        display_date = "%s hour%s ago" % (age.seconds / 3600, 's' if age.seconds > 7200 else '')
    elif age < datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second):
        display_date = 'Today'
    elif age < datetime.timedelta(days=2):
        display_date = 'Yesterday'
    else:
        display_date = dt.strftime("%B %d")

    return display_date


def strip_tags(unsafe_html):
    """ strip all tags from this string which may contain html
    """
    if not unsafe_html:
        return ''

    cleaner = Cleaner(
        page_structure=True,
        links=True,
        safe_attrs_only=True,
        remove_unknown_tags=False,
        allow_tags=['']
    )

    return etree.fromstring(cleaner.clean_html(unsafe_html)).text
