================================================================================
  Common Ground (CG) Co-op Web Site
================================================================================

A web application for the Common Ground Housing Co-op.

This repository is a Django (v. 1.6) web application for the Common Ground
Co-op web site. It is currently in the requirements gathering and development
stage. Feel free to use this for your own housing co-op, or to contribute to
the development process.

.. image:: cg-admin-screenshot.png

.. contents:: Table of Contents


QuickStart
================================================================================

Assuming you have Django 1.6 installed correctly, the following commands will
download the web app, create the database tables, load them with some fake data,
and start the live server.::

    $ git clone https://github.com/jrwdunham/cghousing.git
    $ cd cghousing
    $ python manage.py syncdb
    $ python manage.py loaddata coop/fixtures/fixtureswithusers.json
    $ python manage.py runserver

Voila! Visit http://127.0.0.1:8000/admin/coop/person/ to see a bunch of pretend
co-op members/occupants. Begin exploring the admin site that Django creates for the
co-op model by 

This is all standard Django stuff. See https://docs.djangoproject.com/en/1.6/
for details.


Architecture (thanks to Derek Darling)
================================================================================

- Public

  - About Us

    - Content ("about us subpage")
    - Picture gallery
    - Video gallery
    - Essays and/or blogs (?)
    - Contact Us (Email, Housing requests, Vendor, email hub)
    - Maps (google, or OpenStreetMap)

- Private (authentication required, authorization determines access)

  - Board Page (for all governance materials: minutes, policies, etc.)

    - Menu

      - Board minutes
      - Policies, In Force, including amendments
      - Draft policies and amendments
      - Communications

  - Maintenance Site (for all physical plant records, maintenance requests,
    and disposition (sic))

    - Menu

      - All-member access

        - Unit Database
        - Maintenance Requests
        - Purchase Order Subsystem
        - Inventory


      - Maintenance-only access

        - Discussion

  - Finance (content to be determined)

    - Annual reports (?)

  - Email Hub (for all emailing, including archived email)

    - Email Admin

      - Forms

        - Maintenance request via Email form
        - Housing request via Email form
        - Vendor Email form
        - Other

      - Subsystems
        - Auto-send email subsystem
        - Moderated email subsystem

  - Member Page

    - Maintenance request (directs to maintenance page email forms system (?))
    - Upcoming events
    - Member meeting minutes
    - Discussion groups
    - Etc./other
    - Committees

      - Maintenance (to maintenance page)
      - Grounds (to Grounds page)
      - Social (to Social page)
      - Finance (to Finance page)
      - Other (to Other page)

    - Calendar (automated email reminders, events)


Model
--------------------------------------------------------------------------------

Models to start off with:

- Members
- Committees
- Units
- Pages


These are some ideas for database tables/ models for the application (based on
the architecture):

- Units
- Members
- Committees
- Minutes / Meetings (?)
- Board minutes
- Committee minutes
- Policies (?)
  Contributions (?, i.e., for keeping track of volunteership and involvement)
- Maintenance requests
- Galleries (subtype of pages?)
- Images
- Blogs
- Pages (special and generic pages, markdown)
- Inventory (?)
- Purchase orders
- Member discussion forum
- Maintenance private discussion forum
- Annual reports (finance)
- Communications (?, from board...)
- Emails (part of db?)
- Email forms/templates (part of db?)
- Calendar/Events


Installation Help
================================================================================

Installing Django locally
--------------------------------------------------------------------------------

I used pyenv (https://github.com/yyuu/pyenv) to install Python 2.7.6::

    $ pyenv install 2.7.6

Then I created a virtual Python environment in ~/cg/env/::

    $ cd ~/cg
    $ virtualenv -p ~/.pyenv/versions/2.7.6/bin/python env

I make sure that ``python`` points to my virtual environment in ~/cg/env/ and
then I install the latest official version of Django using pip (1.6.5 at the time
of writing)::

    $ source env/bin/activate
    $ pip install Django


Deploying a Django app on WebFaction
--------------------------------------------------------------------------------

The WebFaction docs are good. See:

- http://docs.webfaction.com/software/django/getting-started.html

  - The screencast guide at the above URL worked. However, it was crucial to
    configure Django properly by following the instructions at
    http://docs.webfaction.com/software/django/getting-started.html#configuring-django

- http://docs.djangoproject.com/en/1.7
- http://docs.webfaction.com/software/django
- http://docs.webfaction.com/software/django/config.html


Detailed instructions
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

1. Create a new (sub)domain, e.g., "new.cghousing.webfactional.com" (via the
   webfaction GUI).

2. Create a new website named, e.g., "cghousing_django" (via the webfaction
   GUI).

3. Create two new applications (via the webfaction GUI):

   i. a Django (v. 1.7.7 Python 2.7) app called, e.g., "cghousing_django" and

   ii. a static (static only, no .htaccess) app called, e.g.,
       "cghousing_django_static" with a URL like
       "http://new.cghousing.webfactional.com/static".

4. Create a PostgreSQL database for the app (via the webfaction GUI), with
   database name and username being, e.g., "cghousing" and "cghousing_admin",
   respectively.

5. Configure Django via SSH. Begin by removing WebFaction's default `myproject`
   and downloading `cghousing` from GitHub::

     ssh cghousing@cghousing.webfactional.com
     cd webapps/cghousing_django
     rm -rf ./myproject
     git clone https://github.com/jrwdunham/cghousing.git

6. Use your favourite text editor (which, obviously, is vim) to make the
   following changes to `cghousing/cghousing/cghousing/settings.py`.

   i. Add our previously created PostgreSQL database to ``DATABASES``.::

        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cghousing',
        'USER': 'cghousing_admin',
        'PASSWORD': '<your_password>',
        'HOST': '',
        'PORT': ''

   ii. Add your domain to allowed hosts.::

        ALLOWED_HOSTS = ['new.cghousing.webfactional.com']

   iii. Configure the static root.::

            STATIC_ROOT = '/home/cghousing/webapps/cghousing_django_static'

7. Configure Apache by editing `apache2/conf/httpd.conf`

   i. Update `WSGIDaemonProcess` to::

        WSGIDaemonProcess cghousing_django processes=2 threads=12 \
        python-path=/home/cghousing/webapps/cghousing_django:\
        /home/cghousing/webapps/cghousing_django/cghousing/cghousing:\
        /home/cghousing/webapps/cghousing_django/lib/python2.7

   ii. Update `WSGIScriptAlias` to::

         WSGIScriptAlias / \
         /home/cghousing/webapps/cghousing_django/\
         cghousing/cghousing/cghousing/wsgi.py

8. Install Django Markdown Deux::

     git clone git://github.com/trentm/django-markdown-deux.git
     cd django-markdown-deux/
     python2.7 setup.py install
     cd ..

     git clone https://github.com/trentm/python-markdown2.git
     cd python-markdown2/
     python2.7 setup.py install
     cd ..

9. Collect the static files, create the database tables (and create an admin
   user when prompted), load a fixture, and restart Apache. Done.::

     cd cghousing/cghousing/
     python2.7 manage.py collectstatic
     python2.7 manage.py syncdb
     python2.7 manage.py loaddata coop/fixtures/fixtureswithusers.json
     cd ../..
     ./apache2/bin/restart

