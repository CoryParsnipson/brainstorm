import os
import re
import random
import datetime

import paths

###############################################################################
# app level defines
###############################################################################
MAX_UPLOAD_SIZE = 104857600  # (1024 * 1024 bits * 100)


###############################################################################
# methods and code common to entire blog app
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


def generate_upload_filename(filename):
    """ given a string (presumably an original filename with extension),
        generate a non-conflicting filename for user uploads
    """
    filename, ext = os.path.splitext(filename)
    filename = "%s-%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), str(int(random.random() * 1000)))

    if ext == '.':
        ext = '.txt'

    return filename + ext


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
        file_dir = paths.MEDIA_IMAGE_ROOT
    elif content_category == "video":
        file_dir = paths.MEDIA_VIDEO_ROOT
    else:
        file_dir = paths.MEDIA_FILE_ROOT

    file_url = os.path.join(file_dir, generate_upload_filename(f.name))

    # enforce file size limit
    if f.size > MAX_UPLOAD_SIZE:
        return False, "%s exceeds maximum upload size!" % f.name

    try:
        os.makedirs(file_dir)
    except OSError:
        # if there is a file with the same name as the intended directory,
        # fail, else directory exists and everything is ok
        if os.path.exists(file_dir) and not os.path.isdir(file_dir):
            return False, "%s cannot be created." % file_dir

    if os.path.exists(file_url):
        # file already exists, return file_url
        return True, file_url

    with open(file_url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True, file_url