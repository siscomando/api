# The `DOMAIN` is commonly put on settings but we preferences was to create
# domains.py file.

from api.schemas import (users_schema, me_schema, issues_schema, comments_schema)


DOMAIN = {
    'users': {
        'url': 'users',
        'datasource': {
            'source': 'user',
                'projection': {'password': 0}
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
        'extra_response_fields': ['email'],
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
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'allowed_read_roles': ['users', 'superusers', 'admins'],
        'schema': issues_schema,
        'cache_control': '', # account cache is not needs.
        'cache_expires': 0,
    },
    'issues_super': {
        'url': 'issue',
        'datasource': {
            'source': 'issue',
        },
        'resource_methods': ['POST'],
        'item_methods': ['PATCH'],
        'allowed_read_roles': ['superusers'],
        'schema': issues_schema,
    },
    'comments': {
        'url': 'comments',
        'datasource': {
            'source': 'comment',
            'default_sort':[('created_at', -1)]
        },
        #'cache_control': '', # account cache is not needs.
        #'cache_expires': 0,
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'schema': comments_schema,
        'embedding': True
    },
    'comments_user': {
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
    'comments_user_edit': {
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
    }
}
