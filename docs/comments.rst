Comments
========

  #. :ref:`list-comments`
  #. :ref:`list-comments-expanded`
  #. :ref:`get-more-comments`
  #. :ref:`list-comments-by-issue`
  #. :ref:`list-comments-by-hashtag`
  #. :ref:`list-comments-by-user`
  #. :ref:`list-comments-with-where`
  #. :ref:`create-a-comment`
  #. :ref:`get-a-single-comment`
  #. :ref:`edit-a-comment`
  #. :ref:`delete-a-comment`


.. _list-comments:

List comments
--------------

.. code::

    GET /comments/

.. code-block:: console

    $ curl -i -u 'u@user.com:pass' http://api.siscomando/api/v2/comments
    HTTP/1.0 200 OK
    Content-Type: application/json

... response:

.. code-block:: javascript

    {
        "_items": [{
            "body": "Any data for only sample. 5871",
            "origin": 0,
            "shottime": null,
            "title": "#SimulatedHashtag",
            "created_at": "Fri, 31 Jul 2015 19:17:42 GMT",
            "author": "55bbc9d5f2c382190d00df05",
            "updated_at": "Fri, 31 Jul 2015 19:17:42 GMT",
            "_links": {
                "self": {
                    "href": "comments/55bbc9d6f2c382189f844848",
                    "title": "Comment"
                }
            },
            "_id": "55bbc9d6f2c382189f844848"
        }, {
            "body": "Any data for only sample. 8791",
            "origin": 0,
            "shottime": null,
            "title": "#SimulatedHashtag",
            "created_at": "Fri, 31 Jul 2015 19:16:21 GMT",
            "author": "55bbc985f2c3821906141f6e",
            "updated_at": "Fri, 31 Jul 2015 19:16:21 GMT",
            "_links": {
                "self": {
                    "href": "comments/55bbc985f2c382189f844847",
                    "title": "Comment"
                }
            },
            "_id": "55bbc985f2c382189f844847"
        }],
        "_links": {
            "self": {
                "href": "comments?max_results=2",
                "title": "comments"
            },
            "last": {
                "href": "comments?max_results=2&page=477",
                "title": "last page"
            },
            "parent": {
                "href": "/",
                "title": "home"
            },
            "next": {
                "href": "comments?max_results=2&page=2",
                "title": "next page"
            }
        },
        "_meta": {
            "max_results": 2,
            "total": 953,
            "page": 1
        }
    }

.. _list-comments-expanded:

List comments expanded
-----------------------
Each `comment` has `author` and `issue` (*optional*) fields. This fields
are based in :doc:`users` and :doc:`issues` resources. Clients can request the
referenced resource to be *expanded* (or embdedded) within the requested document.

For `author` expanded:

.. code::

    GET /comments?embedded={"author":1}

...response:

.. code-block:: javascript

    {
        "_items": [{
            "body": "Any data for only sample. 5871",
            "origin": 0,
            "shottime": null,
            "title": "#SimulatedHashtag",
            "created_at": "Fri, 31 Jul 2015 19:17:42 GMT",
            "author": {
                '_id': '55bbd726f2c3821a40ae9618',
                'email': 'u@user.com',
                'roles': ['users']
            },
            "updated_at": "Fri, 31 Jul 2015 19:17:42 GMT",
            "_links": {
                "self": {
                    "href": "comments/55bbc9d6f2c382189f844848",
                    "title": "Comment"
                }
            },
            "_id": "55bbc9d6f2c382189f844848"
        } // ... intentionally omitted
    }

For `issue` ...

.. code::

    GET /comments?embedded={"issue":1}

.. code-block:: javascript

    {
        "_items": [{
            "body": "Any data for only sample. 8337",
            "origin": 0,
            "shottime": null,
            "title": "#SimulatedHashtag",
            "created_at": "Fri, 31 Jul 2015 20:29:41 GMT",
            "author": "55bbdab4f2c3821a8a6b5c1b",
            "updated_at": "Fri, 31 Jul 2015 20:29:41 GMT",
            "_links": {
                "self": {
                    "href": "comments/55bbdab5f2c3821a768dbff8",
                    "title": "Comment"
                }
            },
            "_id": "55bbdab5f2c3821a768dbff8",
            "issue": {
                "body": "Fora",
                "ugser": "SUNAF",
                "title": "Sisc1",
                "register_orig": "2015RI/0008422",
                "created_at": "Fri, 31 Jul 2015 20:29:40 GMT",
                "ugat": "SUPOP",
                "updated_at": "Fri, 31 Jul 2015 20:29:40 GMT",
                "deadline": 120,
                "closed": false,
                "_id": "55bbdab4f2c3821a768dbff7",
                "classifier": 0,
                "register": "2015RI0008422"
            }
        }]
    }
