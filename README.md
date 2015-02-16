Slacker Paradise
==========

Fuck work; let's skate lololoollololol420errydaaayyyy

Setup
-----

1. Prepare a keyring.txt file (default location is in BASE_DIR, but you can edit filename and location in slackerparadise/settings.py). The format for each token is <name of key>:<key string value>. All lines that do not adhere to this format are considered comments.

2. Make sure the following python packages are installed on the server environment (pip install recommended):

   * django
   * django_imagekit
   * pillow
   * bleach
   * selenium