# The `DOMAIN` is commonly put on settings but we preferences was to create
# domains.py file.

from api.schemas import users_schema, me_schema, issues_schema


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
         'auth_field': 'owner',
         # 'resource_methods': ['PATCH'],
         'item_methods': ['GET', 'PATCH'],
         'allowed_read_roles': ['users'],
         'schema': me_schema
    },
    'issue': {
        'url': 'issues',
        'datasource': {
            'source': 'issue',
        },
        'resource_methods': ['GET'],
        'item_methods': ['GET'],
        'allowed_read_roles': ['users', 'superusers', 'admins'],
        'schema': issues_schema,
    },
    'issue_super': {
        'url': 'issue',
        'datasource': {
            'source': 'issue',
        },
        'resource_methods': ['POST'],
        'item_methods': ['PATCH'],
        'allowed_read_roles': ['superusers'],
        'schema': issues_schema,
    }
}
