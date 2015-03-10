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

    def __init__(self, keyfile=None):
        if not keyfile:
            return

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
                self.keyring[tokens[0]] = tokens[1].replace("\n", "")

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

    def set(self, key, value):
        """ set the value of a specific key
        """
        try:
            old_value = self.keyring[key]
        except KeyError:
            old_value = ""

        self.keyring[key] = value
        return old_value