Comments
========

  #. :ref:`list-comments`
  #. :ref:`list-comments-expanded`
  #. :ref:`get-more-comments`
  #. :ref:`list-comments-by-issue`
  #. :ref:`list-comments-by-hashtag`
  #. :ref:`list-comments-by-user`
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


.. _get-more-comments:

Get more comments (pagination)
-----------------------------
There are two ways to get more comments. First to pass ``page`` query parameter
in the URL.

.. code::

    GET /comments?page=2

Seconde and more programmatic way is handling returned response by :ref:`hypermedia`.
Each query done in the :ref:`resource` that return multiples items will have
:ref:`pagination` info included in the `_links`. You must use it to constructing
your URL.

.. code:: python

    import requests
    import json

    r = requests.get('https://api.siscomando/api/v2/comments', auth=('user', 'pass'))
    data = json.loads(r.text) # convert json output in the python dictionary
    following_link = data['_links']['next']['href'] # catch the link
    print "Relative path to get more comments: ", following_link

.. _list-comments-by-issue:

Get comments by issue
----------------------

.. code::

    GET /comments?where={'issue':<issue_id>}


.. code-block:: console

    $ curl -i -u 'u@user.com:pass' \
    http://api.siscomando/api/v2/comments?where={"issue":"55bfb17cf2c38210424896d4"}
    HTTP/1.0 200 OK
    Content-Type: application/json

.. result:

.. code-block:: javascript

    {
        "_items": [
            {
                "body": "Any data for only sample. 768",
                "origin": 0,
                "shottime": null,
                "title": "#SimulatedHashtag",
                "created_at": "Mon, 03 Aug 2015 18:22:52 GMT",
                "author": "55bfb17bf2c382132220e13c",
                "updated_at": "Mon, 03 Aug 2015 18:22:52 GMT",
                "_links": {
                    "self": {
                        "href": "comments/55bfb17cf2c38210424896d5",
                        "title": "Comment"
                    }
                },
                "_id": "55bfb17cf2c38210424896d5",
                "issue": "55bfb17cf2c38210424896d4"
            }
        ],
        "_links": {
            "self": {
                "href": "comments?where={\"issue\":\"55bfb17cf2c38210424896d4\"}",
                "title": "comments"
            },
            "parent": {
                "href": "/",
                "title": "home"
            }
        },
        "_meta": {
            "max_results": 25,
            "total": 1,
            "page": 1
        }
    }

.. _list-comments-by-hashtag:

List comments by hashtag
-------------------------
This filter is case-insensitive.

.. code::

    GET /comments?hashtag=<string>

.. code-block:: console

    curl -u https://api.siscomando/api/v2/comments?hashtag=AnyHashTag
    # or
    curl -u https://api.siscomando/api/v2/comments?hashtag=ANYHASHTAG

... response:

.. code-block:: javascript

    {
        "_items": [
            {
                "body": "Any data for only sample. 137 <a class=\"hashLink\" eventname=\"hashtag-to-search\" colorlink=\"#47CACC\" href=\"/hashtag/#TestHash\">#TestHash</a>",
                "origin": 0,
                "shottime": null,
                "author": "55c0ca49f2c3821e020f70e7",
                "created_at": "Tue, 04 Aug 2015 14:20:57 GMT",
                "hashtags": [
                    "#AnyHashTag"
                ],
                "updated_at": "Tue, 04 Aug 2015 14:20:57 GMT",
                "_links": {
                    "self": {
                        "href": "comments/55c0ca49f2c3821e00998450",
                        "title": "Comment"
                    }
                },
                "title": "#SimulatedHashtag",
                "_id": "55c0ca49f2c3821e00998450"
            },
            {
                "body": "Any data for only sample. 6413 <a class=\"hashLink\" eventname=\"hashtag-to-search\" colorlink=\"#47CACC\" href=\"/hashtag/#TestHash\">#TestHash</a>",
                "origin": 0,
                "shottime": null,
                "author": "55c0ca1bf2c3821df915684c",
                "created_at": "Tue, 04 Aug 2015 14:20:11 GMT",
                "hashtags": [
                    "#AnyHashTag"
                ],
                "updated_at": "Tue, 04 Aug 2015 14:20:11 GMT",
                "_links": {
                    "self": {
                        "href": "comments/55c0ca1bf2c3821de282b7b1",
                        "title": "Comment"
                    }
                },
                "title": "#SimulatedHashtag",
                "_id": "55c0ca1bf2c3821de282b7b1"
            }
        ],
        "_links": {
            "self": {
                "href": "comments",
                "title": "comments"
            },
            "parent": {
                "href": "/",
                "title": "home"
            }
        },
        "_meta": {
            "max_results": 25,
            "total": 8,
            "page": 1
        }
    }

.. _list-comments-by-user:

List comments by user
----------------------
Note that `author` isn't expanded. This results can be expanded with :ref:`list-comments-expanded`

.. code::

    GET /comments?u=annaibrahim

.. code:: javascript

    {
      "_items": [
          {
              "body": "MSG 04",
              "origin": 0,
              "shottime": null,
              "author": "55b2a943f2c3829eae4b732f",
              "created_at": "Tue, 04 Aug 2015 11:48:54 GMT",
              "hashtags": [
                  "#EverDash"
              ],
              "updated_at": "Tue, 04 Aug 2015 11:48:54 GMT",
              "_links": {
                  "self": {
                      "href": "comments/55c0a6a6f2c3821956c0fbe0",
                      "title": "Comment"
                  }
              },
              "title": "#EverDash",
              "_id": "55c0a6a6f2c3821956c0fbe0"
          }
      ]
      // ... omitted output ...
    }

.. _create-a-comment:

Create a comment
-----------------

.. code::

    POST /comments/new

Parameters
^^^^^^^^^^

==========  ========  ======================================================
Name        Type      Description
==========  ========  ======================================================
issue       string    For associate a `comment` to `issue`. To use issue_id.
body*        string    The content of the new comment.
origin      string    The originator of the comment. Currently supported:
                      0 (default): user's Siscomando; 1: IBM SCCD; 2: Expresso(reserved);
                      3: `Correlacionador` (reserved); 4: Gitlab (reserved)
==========  ========  ======================================================


.. code-block:: console

    $ curl -X POST -u "user@example.com:pass" http://api.siscomando/api/v2/comments/new \
    -d "body=Only you have power to move me"

... response:

.. code-block:: javascript

    {
        "body": "Only you have power to move me",
        "origin": 0,
        "shottime": null,
        "author": "55b2a943f2c3829eae4b732f",
        "created_at": "Wed, 05 Aug 2015 18:21:33 GMT",
        "hashtags": [],
        "updated_at": "Wed, 05 Aug 2015 18:21:33 GMT",
        "_links": {
            "self": {
                "href": "comments/new/55c2542df2c3823234db80a7",
                "title": "Comments_user"
            }
        },
        "_status": "OK",
        "_id": "55c2542df2c3823234db80a7"
    }

*NOTE*:  This response contains `_links` with `comments/new` but this URL (
or resource) only receives `POST` requests. To get a new comment following the
next steps :ref:`get-a-single-comment`.

.. _get-a-single-comment:

Get a single comment
---------------------

.. code::

    GET /comments/<comments_id>

.. code-block:: console

    $ curl -u "user@example.com:pass" http://api.sicomando/api/v2/comments/55c25754f2c38232a0bf54e0

    {
      "body": "Only you have power to move me",
      "origin": 0,
      "shottime": null,
      "author": "55b2a943f2c3829eae4b732f",
      "created_at": "Wed, 05 Aug 2015 18:35:00 GMT",
      "hashtags": [],
      "updated_at": "Wed, 05 Aug 2015 18:35:00 GMT",
      "_links": {
          "self": {
              "href": "comments/55c25754f2c38232a0bf54e0",
              "title": "Comment"
          },
          "collection": {
              "href": "comments",
              "title": "comments"
          },
          "parent": {
              "href": "/",
              "title": "home"
          }
      },
      "_id": "55c25754f2c38232a0bf54e0"
    }

If desires to expand `author` properties use `embedded={"author":1}`.

.. code-block:: console

    $ curl -u "user@example.com:pass" \
    http://api.sicomando/api/v2/comments/55c25754f2c38232a0bf54e0?embedded={"author":1}

... output:

.. code-block:: javascript

    {
        "body": "Only you have power to move me",
        "origin": 0,
        "shottime": null,
        "author": {
            "username": "annaibrahim",
            "first_name": "Horacio",
            "last_name": "Ibrahim",
            "roles": [
                "users",
                "superusers"
            ],
            "md5_email": "c4a2e353943c8ec73d281306712668f3",
            "created_at": "Fri, 24 Jul 2015 18:07:59 GMT",
            "updated_at": "Wed, 29 Jul 2015 21:16:29 GMT",
            "status_online": true,
            "avatar": "http://img.flickr.com/12381394/avatar.png",
            "owner": "55b2a943f2c3829eae4b732f",
            "shortname": "horacioibrahim",
            "_id": "55b2a943f2c3829eae4b732f",
            "email": "horacioibrahim@gmail.com",
            "location": "SUPGS"
        },
        "created_at": "Wed, 05 Aug 2015 18:35:00 GMT",
        "hashtags": [
        ],
        "updated_at": "Wed, 05 Aug 2015 18:35:00 GMT",
        "_links": {
            "self": {
                "href": "comments/55c25754f2c38232a0bf54e0",
                "title": "Comment"
            },
            "collection": {
                "href": "comments",
                "title": "comments"
            },
            "parent": {
                "href": "/",
                "title": "home"
            }
        },
        "_id": "55c25754f2c38232a0bf54e0"
    }


.. _edit-a-comment:

Edit a comment
---------------

.. code::

   GET /comments/edit/<comment_id>

.. code-block:: console

    $ curl -X PATCH -u "user@example.com:pass" \
    http://api.sicomando/api/v2/comments/edit/55c25754f2c38232a0bf54e0 \
    -d "body=This body was changed"

... response:

.. code-block:: javascript

    {
        "body": "This body was changed",
        "origin": 0,
        "shottime": null,
        "author": "55b2a943f2c3829eae4b732f",
        "created_at": "Wed, 05 Aug 2015 18:35:00 GMT",
        "hashtags": [],
        "updated_at": "Wed, 05 Aug 2015 19:24:47 GMT",
        "_links": {
            "self": {
                "href": "comments/edit/55c25754f2c38232a0bf54e0",
                "title": "Comments_user_edit"
            }
        },
        "_status": "OK",
        "_id": "55c25754f2c38232a0bf54e0"
    }

.. _delete-a-comment:

Delete a comment
-----------------
The user can delete your self comments.

.. code::

    DELETE /comments/edit/<comment_id>

.. code-block:: console

    $ curl -X DELETE -u "user@example.com:pass" \
    http://api.sicomando/api/v2/comments/edit/55c25754f2c38232a0bf54e0
    Content-Type: application/json
    Content-Length: 0
