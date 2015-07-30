# This file contains the hooks that fires when `on_pre` or `on_post` Events
# are raised by API.
# See: http://python-eve.org/features.html#eventhooks

import json
import md5
from bson import ObjectId
from flask import abort
from werkzeug.security import generate_password_hash
# app
import api


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

users_hooks = {}
users_hooks['set_username'] = pre_post_users
users_hooks['set_owner'] = post_post_users
