# This file contains the hooks that fires when `on_pre` or `on_post` Events
# are raised by API.
# See: http://python-eve.org/features.html#eventhooks

import datetime
import json
import md5
import re
from bson import ObjectId
from flask import abort, g
from werkzeug.security import generate_password_hash
# app
import api
from utils import wrap_pattern_by_link, generate_token, JSONEncoder



def after_inserted_stars_user(items):
    """ Updates the comment defined in the star's vote.
    """
    comments = api.database.comment
    for item in items:
        comment_id = item['comment']
        pkid = item['_id']
        # update real comment with stars _id
        comments.update({'_id': comment_id},
                {'$push': {'stars': pkid}}
        )

def before_on_insert_users(items):
    """
     Creates new token for new user. `token` must be unique and not can repeated
     as null.
    """

    for item in items:
        item['token'] = generate_token(item['email'])

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

        if 'issue' not in item and 'register' in item and item['register']:
            issue = api.database.issue.find_one({'register': item['register']})
            item['issue'] = issue['_id']
        elif 'issue' in item and 'register' not in item:
            # issue already is within item
            issue = api.database.issue.find_one({'_id': item['issue']})
        else:
            issue = None

        if issue:
            item['title'] = issue['title']
        elif len(item['hashtags']) > 0:
            item['title'] = item['hashtags'][0] # TODO: this could be improved
        else:
            item['title'] = 'no subject'

        if 'issue' in item and item['issue']:
            deltatime = datetime.datetime.utcnow() - issue['created_at']
            item['shottime'] = str(int(deltatime.total_seconds() / 60))
        else:
            item['shottime'] = str(datetime.datetime.today().hour) + 'h'


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

def before_get_comments_search(request, lookup):
    """ Adds $text lookup if parameter search found. This feature only work
    with users and comments.
    """
    search = request.args.get('search', None)
    if search:
        term = {'$search': search}
        lookup['$text'] = term

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

def before_get_users_search(request, lookup):
    """ Adds $regex lookup if parameter search found. This feature only work
    with users and comments.
    """
    search = request.args.get('search', None)
    if search:
        if search.startswith('@'):
            search = search.replace('@', '')
        regx = re.compile(search, re.IGNORECASE)
        lookup['username'] = regx

def post_post_comments_new(request, response):
    """ This hooks fix the returned payload after added a new comment. Because
    the resource used to create has the `comments/new` url. It's only allowed to
    access by POST. Soon isn't possible to make GET in the url built to way
    `comments/<new>/55c2542df2c3823234db80a7`.

    So changes are (samples):

    _links.self.href
    from:
        `comments/new/55c2542df2c3823234db80a7`.
    to:
        `comments/55c2542df2c3823234db80a7`

    author
    from:
        author: 55b2a943f2c3829eae4b732f
    to:
        author: {username: "username" ... }

    """

    if response.status_code == 201:
        data = json.loads(response.data)
        domain = api.resources.DOMAIN # get url of the comments resource.

        if 'author' in data and data['author']:
            lookup = {"_id": ObjectId(data['author'])}
            accounts = api.database.user
            author = accounts.find_one(lookup)
            data['author'] = author
            data['_links']['self']['href'] = "".join([domain['comments']['url'], '/', data['_id']])
            response.data = JSONEncoder().encode(data)

def on_post_get_issues_with_grouped(request, response):
    grouped = request.args.get('grouped', None)

    if grouped and int(grouped) == 1 and response.status_code == 200:
        reducer = "function(obj, prev){prev.issues.push(obj)}"
        # TODO: get only open issues... condition
        # TODO: get with MAX_RESULTS
        grouped_payload = api.database.issue.group(['title'], None,
                            {'issues':[]}, reducer)
        data = json.loads(response.data)
        data[u'_grouped'] = grouped_payload
        response.data = JSONEncoder().encode(data)


users_hooks = {}
users_hooks['set_username'] = pre_post_users
users_hooks['set_owner'] = post_post_users
