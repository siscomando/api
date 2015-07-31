Issues
=======

Issues are an important topic or problem for debate or discussion. In the
SisComando the issues are mainly as ticket of high severity.

  #. :ref:`list-issues`
  #. :ref:`get-more-issues`
  #. :ref:`list-comments-from-issue`
  #. :ref:`get-an-issue`
  #. :ref:`create-an-issue`
  #. :ref:`create-bulk-issues`
  #. :ref:`edit-an-issue`

.. _list-issues:

List issues
------------
List all issues. Remember any requests that returns more than 25 items will be
paginated.

.. code::

    GET /issues


.. _get-more-issues:

Get more issues (pagination)
-----------------------------
There are two ways to get more issues. First to pass ``page`` query parameter
in the URL.

.. code::

    GET /issues?page=2

The more programmatic way is handling returned response by :ref:`hypermedia`.
Each query done in the :ref:`resource` that return multiples items will have
:ref:`pagination` info included in the `_links`. You must use it to constructing
your URL.

.. code:: python

    import requests
    import json

    r = requests.get('https://api.siscomando/api/v2/issues', auth=('user', 'pass'))
    data = json.loads(r.text) # convert json output in the python dictionary
    following_link = data['_links']['next']['href'] # catch the link
    print "Relative path to get more issues: ", following_link


.. _list-comments-from-issue:

List comments from issue
-------------------------

.. code::

    GET /issues/<issue_id>/comments

TODO: In the moment this can be obtained accessing ``/comments?where={"issue_id: 51f63e0838345b6dcd7eabff"}``

.. _get-an-issue:

Get an issue
-------------

.. code::

    GET /issues/<issue_id>

.. _create-an-issue:

Create an issue
-----------------
This is a task to `superusers` role. Therefore there is slightly difference in the
URL (the `s` was suppressed).

.. code::

    POST /issue/

Parameters
^^^^^^^^^^
`* Required`


==========  ========  =======================================
Name        Type      Description
==========  ========  =======================================
title*      string    Title of the issue.
body*       string    Details of the demand.
register*   string    ID of the issue.
classifier  integer   Impact in the business (high, highest)
ugat*       string    Abbrev. for unit or sector for treatment
ugser*      string    Abbrev. for unit or sector responsible
deadline    integer   Time for treatment (default: 120)
closed      boolean   If closed or not (default: False)
==========  ========  =======================================

Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl -H "Content-Type: application/json" -u 'super@superuser.com:pass' \
    -x POST https://api.siscomando/api/v2/issue \
    -d "title=SISCOMEX API"
    -d "body=Siscomex fora do ar"
    -d "register=2015RI/000012831"
    -d "ugat=SUPOP"
    -d "ugser=SUPGS"

... return:

.. code-block:: javascript

    {
      "created_at": "Thu, 30 Jul 2015 19:11:01 GMT",
      "_status": "OK",
      "_links": {
                  "self":{
                            "href": "issue/55ba76c5f2c3820b29360935",
                            "title": "SISCOMEX API"
                          }
                },
      "updated_at": "Thu, 30 Jul 2015 19:11:01 GMT",
      "_id": "55ba76c5f2c3820b29360935"
    }

.. _create-bulk-issues:

Create bulk issues
------------------
In order to reduce the number of loopbacks, a client might also submit multiple
documents with a single request. All it needs to do is enclose the documents in
a JSON list.

.. code::

    POST /issue/

Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl -H "Content-Type: application/json" -u 'super@superuser.com:pass' \
    -X POST https://api.siscomando/api/v2/issue -d '[{document1}, {document2}]'


When multiple documents are submitted the API takes advantage of MongoDB bulk
insert capabilities which means that not only there’s just one single request
traveling from the client to the remote API, but also that only one loopback
is performed between the API server and the database. See more `Bulk Write
Operations <http://docs.mongodb.org/manual/core/bulk-write-operations/>`_.

.. _edit-an-issue:

Edit an issue
--------------

.. code::

    PATCH /issue/<issue_id>

Example Request
^^^^^^^^^^^^^^^^

.. code-block:: console

    $ curl -H "Content-Type: application/json" -u 'super@superuser.com:pass' \
    -X PATCH https://api.siscomando/api/v2/issue/55ba76c5f2c3820b29360935 \
    -d '{"title": "A new Title"}'
