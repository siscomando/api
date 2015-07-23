# This file contains a list of the schemas. It's the representation of the data
# and the basic configuration to enable POST/PATCH methods.
# For me it is redundant because we already have been defined the models.py.
#

users_schema = {
	'email': {
		'type': 'string',
		'required': True,
		'unique': True,
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
	#'username': { See hooks
	#	'type': 'string',
	#}
	'avatar': {
		'type': 'string'
	},
	'roles': {
		'type': 'list',
		'allowed': ['users', 'admins', 'superusers'],
		'default': ['users'],
	},
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
	'register': {
		'type': 'string',
		'required': True,
		'unique': True,
		'maxlength': 50,
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
