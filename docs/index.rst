.. SisComando RESTful API documentation master file, created by
   sphinx-quickstart on Sat Jul 25 21:56:41 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SisComando RESTful API's docs!
==================================================
The REST APIs provide programmatic access to read and write SisComando data.
To insert new Issue, Comment, and more. The REST API identifies SisComando
users using HTTP Basic or Token Authentication. All responses are available
in JSON.

You can improve the quality this product and/or this documentation by posting
a comment with followed by hashtag `#Siscomando` or sending mail to
`horacio dot moreira` or `eduardo dot nascimento` or `marcia dot missias`
at `serpro.gov.br`.

Overview
---------
Below are the documents that describes the resources that make up the official
SisComando API.

1. :ref:`current-version`
2. :ref:`schema`
3. :ref:`resources`
4. :ref:`http-verbs`
5. :ref:`authentication`
6. :ref:`hypermedia`
7. :ref:`pagination`
8. :ref:`requests`
9. :ref:`cross-origin`

.. _current-version:

Current Version
----------------
By default, all request must be sent with ``v2`` prefix::

  http://api.siscomando/api/v2

.. _schema:

Schema
--------
All API access is over HTTPS, and accessed from the ``api.siscomando``. The
current schema is ``https://api.siscomando/api/<v2>/<resource>/[<resource_id>]``
where:

* ``<v2>`` is version.
* ``<resource>`` are the documents as /users, /issues, /comments, etc.
* ``[<resource_id>]`` optional request for specific item.

.. _resources:

Resources
----------
The SisComando is a miner. It can to integrate any kind, from any source,
at massive scale. Currently, the main resources available are:

* :doc:`Users <users>`
* :doc:`Issues <issues>`
* :doc:`Comments <comments>`

.. _http-verbs:

HTTP Verbs
-----------
Where possible, API v2 strives to use appropriate HTTP verbs for each action.
The following table shows the implementation of CRUD operations via REST where
``Collection`` to this purpose can be considered ``Table`` (relational) and
``Documents`` as a ``tuple`` (or row):

======= ========  =================== ==============================
Verb    Action    Database Context    Description
======= ========  =================== ==============================
POST    Create    Document            Used for creating one or multiples.
HEAD    Read      Collection/Document Get header info.
GET     Read      Collection/Document Used for retrieving resources.
PUT     Replace   Document            Used for replacing resource.
PATCH   Update    Document            Update partial (not replace).
DELETE  Delete    Collection/Document Used for deleting.
======= ========  =================== ==============================

.. _authentication:

Authentication
---------------
Customizable Basic Authentication (RFC-2617) is supported. All REST API endpoints
are secured, which means that a client will need to provide the correct
credentials in order to consume the API.

.. code-block:: console

    $ curl -i https://api.sicomando
    HTTP/1.1 401 UNAUTHORIZED
    Please provide proper credentials.

    $ curl -u "user@example.com:password" -i https://api.sicomando
    HTTP/1.1 200 OK


.. _hypermedia:

HATEOAS
--------------------------------------------------------
All resources have ``_links`` properties linking to other resources. This is
provided by support the *Hypermedia as the Engine of Application State* (`HATEOAS <https://en.wikipedia.org/wiki/HATEOAS>`_).
So each ``GET`` responses includes a ``_links`` section. Links provide details
on their ``relation`` relative to the resource being accessed, and a ``title``.
These are meant to provide explicit URLs so that proper API clients don't need
to construct URLs on their own.

.. _pagination:

Pagination
-----------
Requests that return multiple items will be paginated to 25 items by default.
You can specify further pages with the ``?page=<integer>``. You can also set a
custom page size with ``max_results``.

.. code-block:: console

    $ curl -i http://api.siscomando/api/v2/users?max_results=20&page=2
    HTTP/1.1 200 OK

Navigating through the pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The pagination info is included in the ``_links`` (and ``_meta``). It is important
to follow these values instead of constructing your own URLs. You can navigating
through the pages to consume the results. You do this passing the ``page``
parameter. By default, ``page`` always starts at ``1``.

The possible ``_links`` values are:

======  =============================================================
Name    Description
======  =============================================================
self    Shows the URL of the current page.
prev    Shows the URL of the immediate previous page of results.
last    Shows the URL of the last page of results.
next    Shows the URL of the immediate next page of results.
======  =============================================================


... will look like this in the output:


.. code-block:: console

   $ curl -u "s@super.com:123" http://api.siscomando/api/v2/users
   "_links":{
        "self":{
              "href": "users?max_results=10",
              "title": "users"
        },
        "last":{
              "href": "users?max_results=10&page=6",
              "title": "last page"
        },
        "parent":{
              "href": "/",
              "title": "home"
        },
        "next":{
              "href": "users?max_results=10&page=2",
              "title": "next page"
        }
    } # content omitted...
  }

The ``_meta`` field provides pagination data and there is at least one document
being returned. It stores the current ``max_results``, the numbers of items in
a ``total`` and the page number ``page``.


... an example of ``_meta`` output:


.. code-block:: console

   $ curl -u "s@super.com:123" http://api.siscomando/api/v2/users
   ... # omitted for explanation ...
   "_meta":{
        "max_results": 25,
        "total": 58,
        "page": 1
    }

.. _requests:

Requests
---------
Nada pode ser

.. _cross-origin:

Cross Origin Resource Sharing (CORS)
-------------------------------------
`CORS <http://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_ allows web pages to work
REST APIs, something that is usually restricted by most browsers 'same domain' security policy.
The SisComando REST API supports CORS for AJAX requests from any origin.

Here's a sample request sent from a browser hitting ``http://example.com``:

.. code-block:: console

    $ curl -u 's@super.com:123' -i http://api.siscomando/api/v2/users \
    -H "Origin: http://example.com"
    HTTP/1.0 200 OK
    Access-Control-Allow-Origin: http://example.com
    Vary: Origin
    Access-Control-Allow-Headers:
    Access-Control-Expose-Headers:
    Access-Control-Allow-Methods: OPTIONS, HEAD, DELETE, POST, GET

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
