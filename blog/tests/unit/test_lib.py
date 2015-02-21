from django.test import TestCase

import blog.lib as lib


class TestLib(TestCase):
    """ unit tests for blog library functions
    """

    ###########################################################################
    # remove duplicates function tests
    ###########################################################################
    def test_remove_duplicates_no_duplicates(self):
        """ supply remove duplicates with a list containing completely unique
            entries. Should expect the same input back.
        """
        test_input = ['1', '3', '5', '7', 2, 5, 53]

        received_input = lib.remove_duplicates(test_input)

        self.assertEqual(test_input, received_input)

    def test_remove_duplicates_typical(self):
        """ supply remove duplicates with a list that has some duplicates
            (with no more than 2 of each duplicate)
        """
        test_input = [1, 2, 3, 1, 2, 5, 8]
        expected_input = [1, 2, 3, 5, 8]

        received_input = lib.remove_duplicates(test_input)

        self.assertEqual(expected_input, received_input)

    def test_remove_duplicates_all(self):
        """ supply remove duplicates with a list containing only one value
        """
        test_input = [4, 4, 4, 4, 4, 4, 4, 4]
        expected_input = [4]

        received_input = lib.remove_duplicates(test_input)

        self.assertEqual(expected_input, received_input)

    def test_remove_duplicates_no_sort(self):
        """ remove duplicates does not sort entries in any natural order,
            it should just remove duplicates and return the list items in
            the same order
        """
        test_input = [8, 23, 77, 8, 8, 12, 5, 32, 12, 77]
        expected_input = [8, 23, 77, 12, 5, 32]

        received_input = lib.remove_duplicates(test_input)

        self.assertEqual(expected_input, received_input)

    ###########################################################################
    # replace tokens function tests
    ###########################################################################
    def test_replace_tokens_no_replace(self):
        """ supply replace tokens with a string that has no tokens
        """
        token_vals = {}
        test = "there is no token to replace in this string!"
        expected = test

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    def test_replace_tokens_one_token(self):
        """ supply replace tokens with a string that has one token with the
            correct token regex and value is present
        """
        token_vals = {
            'word': 'hella',
        }
        test = "there is {word} token to replace in this string!"
        expected = "there is hella token to replace in this string!"

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    def test_replace_tokens_many_tokens(self):
        """ supply replace tokens with a string that has many tokens, all
            of them are distinct and all of them have values present
        """
        token_vals = {
            'one': 'monkeys',
            'two': 'rocket launcher',
            'three': 'poop',
        }
        test = "I put {one} cake in the {two}. I love {three}!!!"
        expected = "I put monkeys cake in the rocket launcher. I love poop!!!"

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    def test_replace_tokens_duplicate(self):
        """ supply replace tokens with a string that has many instances
            of the same token. The value is present.
        """
        token_vals = {
            'one': 'monkeys',
        }
        test = "One {one}, Two {one}, Three {one}, jumping on the bed"
        expected = "One monkeys, Two monkeys, Three monkeys, jumping on the bed"

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    def test_replace_tokens_no_token(self):
        """ supply replace tokens with a string that has a token which is
            not in the supplied token dictionary

            Note: correct behavior should be to not replace the missing token
        """
        token_vals = {
            'two': 'cake',
        }
        test = "Where is my {one} {two}?!?"
        expected = "Where is my {one} cake?!?"

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    def test_replace_tokens_multiple_no_tokens(self):
        """ supply replace tokens with a string that has multiple distinct
            tokens that are not in the supplied token dictionary
        """
        token_vals = {
        }
        test = "Where is my {one} {two}?!?"
        expected = "Where is my {one} {two}?!?"

        received = lib.replace_tokens(test, token_vals)

        self.assertEqual(expected, received)

    ###########################################################################
    # slugify function tests
    ###########################################################################
    def test_slugify_basic(self):
        """ test slugify, typical case
        """
        test_string = "This is a test string."
        expected = "this-is-a-test-string"

        received = lib.slugify(test_string)

        self.assertEqual(expected, received)

    def test_slugify_truncate(self):
        """ supply slugify a string that would be truncated to 20 characters
        """
        test_string = "omg this is such a long string it will definitely be truncated"
        expected = "omg-this-is-such-a"

        received = lib.slugify(test_string, max_len=20)

        self.assertEqual(expected, received)

    def test_slugify_alphanumeric(self):
        """ supply slugify a string that needs to be pruned of non-alphanumeric
            characters
        """
        test_string = "what The !@@$$K/:+??! sdffkdksf omg bbq"
        expected = "what-the-k-sdffkdksf"

        received = lib.slugify(test_string, max_len=20)

        self.assertEqual(expected, received)

    def test_slugify_alphanumeric2(self):
        """ supply slugify where the original string consists entirely
            of non-alphanumeric characters

            Note: current behavior is to return an empty string
        """
        test_string = "@@@@@@@@@@!!!!!!!!!!"
        expected = ""

        received = lib.slugify(test_string)

        self.assertEqual(expected, received)

    def test_slugify_alphanumerica3(self):
        """ truncate non-alphanumeric characters until you reach valid ones
        """
        test_string = "!#^#$$$&#^*$(   ^#$^#$^^#$^^#%%slackerparadise Rulez!!"
        expected = "slackerparadise-rulez"

        received = lib.slugify(test_string, max_len=25)

        self.assertEqual(expected, received)

    ###########################################################################
    # truncate function tests
    ###########################################################################
    def test_truncate(self):
        self.fail('to be implemented')

    ###########################################################################
    # generate_upload_filename function tests
    ###########################################################################
    def test_generate_upload_filename(self):
        self.fail('to be implemented')

    ###########################################################################
    # upload_file function tests
    ###########################################################################
    def test_upload_file(self):
        self.fail('to be implemented')

    ###########################################################################
    # get_center_coord function tests
    ###########################################################################
    def test_get_center_coord(self):
        """ supply rect which is bigger than box in both dimensions
        """
        rect = (600, 300)
        box = (200, 100)
        expected = ((rect[0] - box[0]) / 2, (rect[1] - box[1]) / 2)

        received = lib.get_center_coord(box, rect)

        self.assertEqual(expected, received)

    def test_get_center_coord_same_size(self):
        """ supply rect which is the same size as box
        """
        rect = (200, 200)
        box = rect
        expected = (0, 0)

        received = lib.get_center_coord(box, rect)

        self.assertEqual(expected, received)

    def test_get_center_coord_box_bigger(self):
        """ supply rect which is smaller than box in both dimensions
        """
        rect = (163, 929)
        box = (4003, 1203)
        expected = (0, 0)

        received = lib.get_center_coord(box, rect)

        self.assertEqual(expected, received)

    def test_get_center_coord_box_bigger_x(self):
        """ supply rect with smaller x dimension than box
        """
        rect = (400, 500)
        box = (600, 300)
        expected = (0, 100)

        received = lib.get_center_coord(box, rect)

        self.assertEqual(expected, received)

    def test_get_center_coord_box_bigger_y(self):
        """ supply rect with smaller y dimension than box
        """
        rect = (900, 200)
        box = (600, 300)
        expected = (150, 0)

        received = lib.get_center_coord(box, rect)

        self.assertEqual(expected, received)

    ###########################################################################
    # resize_image function tests
    ###########################################################################
    def test_resize_image(self):
        self.fail('to be implemented')

    ###########################################################################
    # create_pagination function tests
    ###########################################################################
    def test_create_pagination(self):
        self.fail('to be implemented')

    ###########################################################################
    # create_paginator function tests
    ###########################################################################
    def test_create_paginator(self):
        self.fail('to be implemented')