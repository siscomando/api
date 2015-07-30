Users
======

  #. :ref:`single-user`
  #. :ref:`authenticated-user`
  #. :ref:`update-authenticated-user`
  #. :ref:`all-users`

.. _single-user:

Get a single user
------------------

.. code::

    GET /users/<ID_USER>

or

.. code::

    GET /users/<username>

Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl https://api.sicomando/api/v2/users/55b2a8f3f2c3829ea0263b76 \
    -u "user@example.com:123" -H "Content-Type: application/json"
     {
         "username": "AntonioMadelena_1",
         "roles": [
         ],
         "md5_email": "8988e63d3e90084b199f8c8f280b5068",
         "created_at": "Fri, 24 Jul 2015 18:06:59 GMT",
         "updated_at": "Thu, 01 Jan 1970 00:00:00 GMT",
         "status_online": true,
         "_links": {
             "self": {
                 "href": "users/55b2a8f3f2c3829ea0263b76",
                 "title": "User"
             },
             "collection": {
                 "href": "users",
                 "title": "users"
             },
             "parent": {
                 "href": "/",
                 "title": "home"
             }
         },
         "shortname": "AntonioMadelena_1",
         "_id": "55b2a8f3f2c3829ea0263b76",
         "email": "AntonioMadelena_1@Madelena.com"
     }

.. _authenticated-user:

Get the authenticated user
--------------------------

.. code::

    GET /me/


Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl https://api.sicomando/api/v2/me/ \
    -u "user@example.com:123" -H "Content-Type: application/json"
    {
        "username": "User Example",
        "roles": ["users"
        ],
        "md5_email": "8988e63d3e90084b199f8c8f280b5098",
        "created_at": "Fri, 21 Jul 2015 08:06:59 GMT",
        "updated_at": "Thu, 01 Jan 1970 00:00:00 GMT",
        "status_online": true,
        "_links": {
            "self": {
                "href": "users/55b2a8f3f2c3829ea0263b80",
                "title": "User"
            },
            "collection": {
                "href": "users",
                "title": "users"
            },
            "parent": {
                "href": "/",
                "title": "home"
            }
        },
        "shortname": "user",
        "_id": "55b2a8f3f2c3829ea0263b80",
        "email": "user@example.com"
    }

.. _update-authenticated-user:

Update the authenticated user
------------------------------

.. code::

    PATCH /me/<ID_USER>

Parameters
^^^^^^^^^^

==========  ========  ===============================
Name        Type      Description
==========  ========  ===============================
first_name  string    The new first name of the user.
last_name   string    The new last name of the user.
location    string    The new location of the user.
username    string    The visible username.
avatar      url       The new URL to access avatar.
==========  ========  ===============================


Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl -X PATCH https://api.sicomando/api/v2/me/1234 \
    -u "user@example.com:123" -H "Content-Type: application/json" \
    -d "first_name=Anna" \
    -d "last_name=Ibrahim" \
    -d "location=SUPGS/GSIAU" \
    -d "username=annaibrahim" \
    -d "avatar=http://img.flickr.com/12381394/avatar.png"

.. _all-users:

Get all users
--------------

.. code::

    GET /users/


Example Request
^^^^^^^^^^^^^^^^
In the case, ``max_results`` was used for to improvement of the explanation. Note
that the payload returns ``_items``, ``_links`` and ``_meta`` where ``_items``
is the content and the others are metadata.

.. code-block:: console

    $ curl https://api.sicomando/api/v2/users?max_results=1 \
    -u "user@example.com:123" -H "Content-Type: application/json"
    {
        "_items": [
            {
                "roles": [
                    "superusers"
                ],
                "created_at": "Thu, 01 Jan 1970 00:00:00 GMT",
                "updated_at": "Thu, 01 Jan 1970 00:00:00 GMT",
                "_links": {
                    "self": {
                        "href": "users/55b748c1f2c382ba73517c79",
                        "title": "User"
                    }
                },
                "_id": "55b748c1f2c382ba73517c79",
                "email": "s@super.com"
            }
        ],
        "_links": {
            "self": {
                "href": "users?max_results=1",
                "title": "users"
            },
            "last": {
                "href": "users?max_results=1&page=58",
                "title": "last page"
            },
            "parent": {
                "href": "/",
                "title": "home"
            },
            "next": {
                "href": "users?max_results=1&page=2",
                "title": "next page"
            }
        },
        "_meta": {
            "max_results": 1,
            "total": 58,
            "page": 1
        }
    }
