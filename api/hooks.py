# This file contains the hooks that fires when `on_pre` or `on_post` Events
# are raised by API.
# See: http://python-eve.org/features.html#eventhooks

import json
import md5
import re
from bson import ObjectId
from flask import abort
from werkzeug.security import generate_password_hash
# app
import api
from utils import wrap_pattern_by_link


def before_on_insert_comments(items):
    """
    The post data sent by client is plaintext because is needs to convert the
    `#text` and `@mention` for links within body field. This function also set
    `title` if `issue_id` not exists.
    """
    preg = r'(#\w+)'
    for item in items:
        item['hashtags'] = re.findall(preg, item['body'])
        item['body'] = wrap_pattern_by_link(preg, item['body'])
    # TODO: set_title

def before_on_update_comments(items):
    # TODO: set_shottime
    pass

def before_on_insert_issue(items):
    """
    This action normalize the register number removing slash ('/') and
    copy the original data to field register_orig. This works with one or
    bulk inserts.
    """
    for i in items:
        i['register_orig'] = i['register']
        i['register'] = i['register'].replace('/', '')

def before_returning_items_from_me(response):
    """
    """
    output = response['_items'][0]

    # cleaner and keeping id
    for k, v in response.items():
        del(response[k])

    for k, v in output.items():
        response[k] = v

def before_get_comments_hashtags(request, lookup):
    """ Makes the filter `$in` in the hashtag `ListField`.
    """
    tag = request.args.get('hashtag', None)
    u = request.args.get('u', None)
    if tag:
        hashtag = ''.join(['#', tag])
        patter = re.compile(r'{}'.format(tag), flags=re.IGNORECASE)
        lookup['hashtags'] = {'$in': [patter]}

    if u:
        local_lookup = {'username': u}
        accounts = api.database.user
        author = accounts.find_one(local_lookup)
        lookup['author'] = author['_id']

def pre_post_users(request):
    """Adds at the body data that was send by user's API the `username`
    field. The username is the localpart from email address."""

    if not request.json:
        abort(401, "The body data isn't a JSON format.")

    json_data = request.get_json()
    username = json_data['email'].split('@')[0]
    username = username.replace('.', '')
    json_data['username'] = username
    json_data['password'] = generate_password_hash(json_data['password'])
    api.app.test_client().post(data=json.dumps(json_data),
                    content_type='application/json')

def post_post_users(request, payload):
    """ Sets the field `owner` with _id of the user recently created. This is a
    workaround due at `auth_field` when setted to `_id` to receive the
    superuser's _id when to create or edit the user.

    ::Explanation::
    Only `superusers` roles can create a new user. With Eve framework is possible
    to use `auth_field` feature to add an author for document created. But we
    wants that the `auth_field` of the `User` model be the `_id` of the
    recently user created instead superuser.
    """
    if payload.status_code == 201:
        accounts = api.database.user
        # recently created. to add _id for owner field.
        data = payload.response[0]
        json_data = json.loads(data)
        object_id = json_data['_id']
        accounts.update({'_id': ObjectId(object_id)},
                        {'$set': {
                            'owner': ObjectId(object_id),
                            'md5_email': md5.md5(json_data['email']).hexdigest()
                        }})

def post_post_comments_new(request, payload):
    """ This hooks fix the returned payload after added a new comment. Because
    the resource used to create it is `comments/new` that only is allowed to
    access by POST. So `comments/new/55c2542df2c3823234db80a7` isn't possible.
    This hook will return `comments/55c2542df2c3823234db80a7`.
    """
    # TODO: make it
    pass


users_hooks = {}
users_hooks['set_username'] = pre_post_users
users_hooks['set_owner'] = post_post_users
