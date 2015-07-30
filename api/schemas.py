# This file contains a list of the schemas. It's the representation of the data
# and the basic configuration to enable POST/PATCH methods.
# For me it is redundant because we already have been defined the models.py.
#

users_schema = {
	'email': {
		'type': 'string',
		'required': True,
		'unique': True,
		'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
	},
	'first_name': {
		'type': 'string',
		'maxlength': 50,
	},
	'last_name': {
		'type': 'string',
		'maxlength': 50,
	},
	'password': {
		'type': 'string',
		'required': True,
	},
	'location': {
		'type': 'string',
		'maxlength': 25,
	},
	'username': { # See hooks
		'type': 'string',
		'unique': True
	},
	'avatar': {
		'type': 'string'
	},
	'roles': {
		'type': 'list',
		'allowed': ['users', 'admins', 'superusers'],
		'default': ['users'],
	},
	'user_id': {
		'type': 'string',
		'readonly': True
	},
	'md5_email': {
		'type': 'string',
		'readonly': True,
		'default': 'empty'
	}
}
me_schema = {
	'email': {
		'type': 'string',
		'readonly': True,
	},
	'first_name': {
		'type': 'string',
		'maxlength': 50,
	},
	'last_name': {
		'type': 'string',
		'maxlength': 50,
	},
	'location': {
		'type': 'string',
		'maxlength': 25,
	},
	'username': { # See hooks
		'type': 'string',
		'unique': True
	},
	'avatar': {
		'type': 'string'
	},
	'roles': {
		'type': 'list',
		'allowed': ['users', 'admins', 'superusers'],
		'default': ['users'],
		'readonly': True,
	},
	'md5_email': {
		'type': 'string',
		'readonly': True,
		'default': 'empty'
	}
}
issues_schema = {
	'title': {
		'type': 'string',
		'required': True,
		'maxlength': 150,
	},
	'body': {
		'type': 'string',
		'required': True,
	},
	'register': { # to save register_orig
		'type': 'string',
		'required': True,
		'unique': True,
		'maxlength': 50,
	},
	'register_orig': {
		'type': 'string',
		'readonly': True
	},
	'classifier': {
		'type': 'integer',
		'default': 0,
	},
	'ugat': {
		'type': 'string',
		'maxlength': 12,
		'required': True,
	},
	'ugser': {
		'type': 'string',
		'maxlength': 12,
		'required': True,
	},
	'deadline': {
		'type': 'integer',
		'default': 120
	},
	'closed': {
		'type': 'boolean',
		'default': False
	}
}
comments_schema = {}
