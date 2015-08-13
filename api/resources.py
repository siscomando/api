# The `DOMAIN` is commonly put on settings but we preferences was to create
# domains.py file.

from werkzeug.security import check_password_hash
from flask import abort
from eve.auth import BasicAuth
import api
from api.schemas import (users_schema, me_schema, issues_schema, comments_schema,
        accounts_schema, stars_schema)


class ApiBasicAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resources, method):
        app = api.app
        accounts = app.data.driver.db['user']
        lookup = {'email': username}

        if allowed_roles:
            # only retrieve a user if his roles match
            lookup['roles'] = {'$in': allowed_roles}

        account = accounts.find_one(lookup) # Query here

        # workaround to block empty [] roles. Temporally implementation.
        # teorically this not needs.
        if account and 'roles' in account and len(account['roles']) == 0:
        	abort(401, description="The action's user not have roles defined.")

        # set 'auth_field' value to owners documents.
        if account and '_id' in account:
        	self.set_request_auth_value(account['_id'])

        if account:
        	if check_password_hash(account['password'], password):
        		return True
        	else:
        		abort(401,
        		description="Please provide proper credentials (authentication)")
        	return account
        else:
        	# This will to raise: 'Please provide proper credentials'. That can
        	# to be i. user not exists, ii. roles not macth or
        	# iii. password invalid.
        	return False

DOMAIN = {
    'accounts': {
        'url': 'login',
        'datasource': {
            'source': 'users',
        },
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'email'
        },
        'cache_control': '',
        'cache_expires': 0,
        'resource_methods': ['GET'],
        'auth_field': 'owner',
        'schema': accounts_schema,
        'authentication': ApiBasicAuth
    },
    'users': {
        'url': 'users',
        'datasource': {
            'source': 'user',
            'projection': {'password': 0, 'token': 0}
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'resource_methods': ['GET', 'POST', 'DELETE'],
        'item_methods': ['GET', 'DELETE'],
        'schema': users_schema, # EVEMongoengine?
        'allowed_read_roles': ['users', 'superusers'],
        'allowed_item_read_roles': ['users', 'superusers'],
        'allowed_item_write_roles': ['superusers'],
        'allowed_write_roles': ['superusers'],
        'extra_response_fields': ['email', 'token'],
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'username'
        },
         # 'auth_field': 'owner', # bomb to backend
    },
    'me': {
        'url': 'me',
        'datasource': {
            'source': 'user',
            'projection': {'password': 0}
        },
         # It's name is `owner` instead `author` because the author was a superusers
         'auth_field': 'owner',
         # 'resource_methods': ['PATCH'],
         'item_methods': ['GET', 'PATCH'],
         'allowed_read_roles': ['users'],
         'schema': me_schema
    },
    'issues': {
        'url': 'issues',
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'register'
        },
        'datasource': {
            'source': 'issue',
        },
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['GET', 'PATCH', 'DELETE'],
        'allowed_item_write_roles': ['superusers'],
        'allowed_write_roles': ['superusers'],
        'allowed_read_roles': ['users', 'superusers', 'admins'],
        'schema': issues_schema,
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
    },
    'issues_super': { # TODO to find this reference issues_super (and issues/new)
        'url': 'issues/new',
        'datasource': {
            'source': 'issue',
        },
        'resource_methods': ['POST'],
        'item_methods': ['PATCH'],
        'allowed_read_roles': ['superusers'],
        'schema': issues_schema
    },
    'comments': {
        'url': 'comments',
        'datasource': {
            'source': 'comment',
            'default_sort':[('created_at', -1)]
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'schema': comments_schema,
        'embedding': True
    },
    'comments_user': { # created to support auth_field
        'url': 'comments/new',
        'datasource': {
            'source': 'comment'
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'resource_methods': ['POST'],
        'auth_field': 'author',
        'extra_response_fields': comments_schema.keys(),
        'schema': comments_schema,
    },
    'comments_user_edit': { # created only to coherence url.
        'url': 'comments/edit',
        'datasource': {
            'source': 'comment'
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'item_methods': ['PATCH', 'DELETE'],
        'auth_field': 'author',
        'extra_response_fields': comments_schema.keys(),
        'schema': comments_schema,
    },
    'stars' : {
        'datasource': {
            'source': 'stars',
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'url': 'stars',
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'schema': stars_schema
    },
    'stars_user' : { # create to support auth_field
        'datasource': {
            'source': 'stars',
        },
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
        'url': 'stars/new',
        'resource_methods': ['POST'],
        'auth_field': 'voter',
        'extra_response_fields': stars_schema.keys(),
        'schema': stars_schema
    },
}
