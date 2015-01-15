import os
import random
import datetime

# common.py
# contains common functions and structures used between multiple apps


class Globals:
    """ site-wide constants and global values
    """
    def __init__(self):
        return


class KeyRing:
    """ key value storage of sensitive information and passwords for the site
    """

    keyring = {}

    def __init__(self, keyfile):
        f = None

        try:
            # open given filename (assume relative to cwd if not absolute path)
            f = open(keyfile)
        except IOError as e:
            print "KeyRing: " + e.message
            return

        for line in f:
            tokens = line.split(":")

            if len(tokens) == 2:
                self.keyring[tokens[0]] = tokens[1]

        f.close()

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        kr_string = ["KEYRING:"]

        for key, val in self.keyring.items():
            kr_string.append(key + " = " + val)

        return "\n".join(kr_string)

    def get(self, key):
        """ given a string to match a key, return the associated value

        :param key:
        :return: string containing key's value
        """
        try:
            return self.keyring[key]
        except KeyError:
            return ""


def generate_upload_filename(filename):
    """ given a string (presumably an original filename with extension),
        generate a non-conflicting filename for user uploads
    """
    filename, ext = os.path.splitext(filename)
    filename = "%s-%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), str(int(random.random() * 1000)))

    if ext == '.':
        ext = '.txt'

    return filename + ext