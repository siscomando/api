# This file contains a list of the schemas. It's the representation of the data
# and the basic configuration to enable POST/PATCH methods.
# For me it is redundant because we already have been defined the models.py.
#

accounts_schema = {
	'email': {
		'type': 'string',
		'unique': True,
		'readonly': True
	},
	'password': {
		'type': 'string',
		'readonly': True
	},
	'token': {
		'type': 'string',
		'unique': True,
		'readonly': True
	}
}
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
	'md5_email': {
		'type': 'string',
		'readonly': True,
		'default': 'empty'
	},
	'token': {
		'type': 'string',
		'readonly': True
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

stars_schema = {
	'voter': {
		'type': 'objectid',
		'data_relation': {
			'resource': 'users',
			'field': '_id',
			'embeddable': True
		},
		'readonly': True # voter is captured by current user.
	},
	'score': {
		'type': 'integer',
		'default': 0,
	},
	'comment': {
		'type': 'objectid',
		'data_relation': {
			'resource': 'comments',
			'field': '_id',
			'embeddable': True
		},
	}
}

# stand by when to migrate for MongoDB
stars_embedded = {
	'stars': {
		'type': 'list',
		'schema': {
			'type': 'dict',
			'schema': {
				'voter': {
					'type': 'objectid',
					'data_relation': {
						'resource': 'users',
						'field': '_id',
						'embeddable': True
					}
				},
				'score': {
					'type': 'integer',
					'default': 0,
				},
			}
		}
	}
}

comments_schema = {
	# Embedded or ReferenceField
	'issue': {
		'type': 'objectid',
		'data_relation': {
			'resource': 'issues',
			'field': '_id',
			'embeddable': True
		},
		'nullable': True
	},
	'register': {
		'type': 'string',
		'data_relation': {
			'resource': 'issues',
			'field': 'register',
			'embeddable': True
		},
		'nullable': True
	},
	'author': {
		'type': 'objectid',
		'data_relation': {
			'resource': 'users',
			'field': '_id',
			'embeddable': True
		},
		'readonly': True
	},
	# 'stars': this is inject by hooks
	# TODO: expand sublevels as voter.
	'stars': {
		'type': 'list',
		'schema': {
			'type': 'objectid',
			'data_relation': {
				'resource': 'stars',
				'field': '_id',
				'embeddable': True
			}
		},
		'readonly': True
	},
	# Ordinary fields
	'shottime': {
		'type': 'integer',
		'default': None,
		'nullable': True,
		'readonly': True
	},
	'body': {
		'type': 'string',
		'required': True
	},
	'origin': {
		'type': 'integer',
		# Integer is better: 0: sc | 1: sccd | 2: email
		'min': 0,
		'max': 2,
		'default': 0
	},
	# title isn't required when hashtag or issue_id exists.
	'title': {
		'type': 'string',
		'maxlength': 120,
	},
	'mentions_users': {
		'type': 'list',
		'readonly': True
	},
	'hashtags': {
		'type': 'list',
		'readonly': True
	}
}
