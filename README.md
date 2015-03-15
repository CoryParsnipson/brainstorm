Slacker Paradise
==========

Fuck work; let's skate lol

Hey You. Yeah You. The One Looking At Me Like An Idiot. Don't Point Its Rude
--------------------------------------------------------------------------

Hello, Human:

If you are reading this then I, Cory Parsnipson, have most certainly died in a terribly gruesome way. The future of Slacker Paradise is in grave danger and it is up to *you* to restore it to its once majestic glory! YOU ARE THE CHOSEN ONE. \*sparkle\* Please, you're our only hope.
  
Set up a VirtualEnv, You Freaking Dope
--------------------------------------

Look at requirements.txt. Look at it. Can you get all these things together and put them in a virtual environment? What do you mean, "no"? Fuck off, this is your job.

Slacker Paradise was written with Python 2.7.8. Go to the easy_install site, install pip, and then install virtualenv and everything else you need.

Slacker Paradise has two settings files, local and production. Local is the development server, using an sqlite3 backend, and Production uses the postgres database and python packages, along with Amazon S3 storage keys. This is accessible inside the python script with "from django.conf import settings".

If you are running locally using the Django manage.py runserver, you will need a text file containing all the django secret key, aws access key, etc in a file specified by the common.KeyRing module. For the production settings, you need to configure a heroku app.

Uh, I probably shouldn't say this but what the hell. The keys in the keyring file are as follows:

* DJANGO_SECRET_KEY
* AWS_ASSOCIATE_TAG
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* S3_BUCKET_NAME

What was that? Values?? Ha! What a maroon. I'm not going to tell you those. Go find them yourself, you lazy bum.

Wait What the Hell is Heroku? Some Kinda Chinky Thing??
-------------------------------------------------------

Shut up SHUT UP god you are the worst chosen one ever. Stop screwing around and go sign up for an account and install the heroku toolbelt and make an app named "slackerparadise" or something. You need to set the environment variables using "heroku config:set [var]=[val]" (all the same ones as in the keyring file).

Don't forget to set up the database. Your app should be on a cedar stack, so run "heroku addons:add heroku-postgresql". After that, populate the database schema with "heroku run python manage.py migrate".

Create a Superuser; Bring Me Back To Life
-----------------------------------------

"heroku run python manage.py createsuperuser". These are your login credentials.

MWAHAHAHAHAHA Now Kill Them All KILL THEM ALL
---------------------------------------------