SisComando API
==============

The RESTful API for `SisComando WebApp <https://github.com/siscomando/webapp>`_. This API uses
`python-eve <http://python-eve.org/>`_ a Python REST API Framework. It work fine with MongoDB
where we're using it. But you can use relational-SQL data model see
`eve-sqlalchemy <http://eve-sqlalchemy.readthedocs.org/en/stable/>`_.

Requirements
-------------
  * Python 2.7
  * Redis
  * MongoDB

Install
-------------
Follows steps.

1. Create virutalenv
::

 $ virtualenv siscomando_api
 $ cd siscomando_api/
 $ source bin/activate

2. Download API
::

 $ git clone https://github.com/siscomando/api.git
 $ cd api/
 
3. Install Requirements Libs
::

 $ pip install -r requirements.txt

4. To change `settings.py` if necessary. (e.g: database name, etc)

5. Exports EVE_SETTINGS as environment variable:
::

 # if you are inside api folder from git.
 # api/
 # --- api/settings.py
 $ export EVE_SETTINGS=`pwd`/api/settings.py

6. Runs app:
::

 # For production
 $ python manage.py runserver
 # For development. With default web server of the Flask.
 $ python manage.py runserver_sync

Quick Usage
-----------
By default all requests must be authenticated. You needs to create at least one
user to access/request data from API.

1. Adding superuser
::

 # Inside api/ (parent) and with virtualenv activated
 $ python manage.py addsuperuser
 The s@super.com:123 was created. You can change it later.

2. Test it
::

 $ curl -H "Content-Type: application/json" -u 's@super.com:123' \
 http://localhost:9014/api/v2/users
 {"_items": [{"roles": ["superusers"], ... , "email": "s@super.com"}]}
