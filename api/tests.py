
import unittest
import requests
import json
import md5
import random
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash

DATABASE = MongoClient()['dev_scdb']
MAX_RESULTS = 25

class ApiTests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		conn = MongoClient()
		cls.database = conn['dev_scdb']
		# Add superuser
		cls.s = cls.database.user.insert({'email':'s@super.com',
		    'password': generate_password_hash('123'),
			'roles': ["superusers"]})
		# Add ordinary user
		cls.u = cls.database.user.insert({'email':'u@user.com',
					'password': generate_password_hash('123'),
					'roles': ["users"]})
		# simple join string to url
		host = 'http://localhost:9014/api/v2/'
		cls.concat = lambda cls, rp: "{}{}".format(host, rp) # rp = relative path

	@classmethod
	def tearDownClass(cls):
		cls.database.user.remove({'_id': cls.s});
		cls.database.user.remove({'_id': cls.u});


class UserTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'mariolago_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}

	def tearDown(self):
		# TODO: delete users created in the cases.
		pass

	def test_get_not_authenticated(self):
		""" tests to access API without is authenticated. """
		r = requests.get(self.concat('users'))
		self.assertEqual(r.status_code, 401)
		r = requests.post(self.concat('users'), json=self.data)
		self.assertEqual(r.status_code, 401)
		# adding simple user
		r = requests.post(self.concat('users'), json=self.data,
			auth=('s@super.com', '123'))
		data = json.loads(r.text)
		# trying get item
		link = 'users/{}'.format(data['_id'])
		link_p = 'users/{}'.format(data['_id'])
		r = requests.get(self.concat(link))
		self.assertEqual(r.status_code, 401)
		link = 'me/{}'.format(data['_id'])
		r = requests.get(self.concat(link))
		self.assertEqual(r.status_code, 401)
		# patch on /me
		r = requests.patch(self.concat(link), json={'first_name': 'Blue'})
		link = 'users/{}'.format(data['_id'])
		r = requests.get(self.concat(link), auth=('s@super.com', '123'))
		data = json.loads(r.text)
		self.assertNotIn('first_name', data)
		# patch on /users
		r = requests.patch(self.concat(link_p), json={'first_name': 'Blue'})
		self.assertEqual(r.status_code, 405)



	def test_get_users(self):
		""" tests if returned lists is less than 25 items. Authentication is
		required.
		"""
		r = requests.get(self.concat('users'), auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		self.assertNotIn('password', account)
		self.assertLessEqual(len(data), 25)

	def test_get_item_users(self):
		""" tests to get item by HATEOAS (forward links) for users results."""
		r = requests.get(self.concat('users'), auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		data = json_data['_items']
		account = data[0]
		hateoas_link = account['_links']['self']['href']
		r = requests.get(self.concat(hateoas_link),
			auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		strip_url = hateoas_link.split('/')
		self.assertEqual(json_data['_id'], strip_url[-1])

	def test_get_users_next_page(self):
		""" tests if exists next_link pages.
		"""
		r = requests.get(self.concat('users'), auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		links = json_data['_links']
		next_link = links['next']['href']
		r = requests.get(self.concat(next_link),
			auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		data = json_data['_items']
		self.assertGreaterEqual(len(data), 1)

	def test_get_users_last_page(self):
		""" tests if exists last pages.
		"""
		r = requests.get(self.concat('users'), auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		links = json_data['_links']
		total = json_data['_meta']['total']
		next_link = links['last']['href']
		last_page = next_link.split('?')
		last_page = last_page[-1]
		last_page = int(last_page.split('=')[1])
		r = requests.get(self.concat(next_link),
			auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		data = json_data['_items']
		qtd_last_page = total - ((last_page - 1) * MAX_RESULTS)
		self.assertEqual(len(data), qtd_last_page)

	def test_get_me(self):
		""" Tests access in the /me """
		# adding user with users role
		r = requests.post(self.concat('users'), auth=('s@super.com', '123'),
			json=self.data)
		# recently user go to access /me
		r = requests.get(self.concat('me'), auth=(self.data['email'], '123'))
		data = json.loads(r.text)
		self.assertEqual(data['email'], self.data['email'])

	# PATCH tests
	def test_patch_me(self):
		""" tests changes in own user.
		"""
		""" Tests access in the /me """
		# adding user with users role
		r = requests.post(self.concat('users'), auth=('s@super.com', '123'),
			json=self.data)
		# recently user go to access /me
		user_id = json.loads(r.text)['_id']
		link = 'me/{}'.format(user_id)
		r = requests.patch(self.concat(link), auth=(self.data['email'], '123'),
			json={'first_name': 'Mario', 'last_name': 'Lago',
				'location': 'SUPGS/GSAUD/GSIAUI', 'avatar': 'http://uol.com.br/',
				})
		r = requests.get(self.concat('me'), auth=(self.data['email'], '123'))
		data = json.loads(r.text)
		self.assertEqual(data['first_name'], 'Mario')

	def test_patch_edit_another_user_by_me(self):
		""" tests changes in own user.
		"""
		# adding user 1
		r1 = requests.post(self.concat('users'), auth=('s@super.com', '123'),
			json=self.data)
		# adding user 2
		r2 = requests.post(self.concat('users'), auth=('s@super.com', '123'),
			json={'email': 'singleuser@user.com', 'password': '123',
				'roles':['users']})
		# recently user go to access /me
		user_id = json.loads(r1.text)['_id']
		link = 'me/{}'.format(user_id)
		# PATCH with id from r1 and accessing by r2 user.
		r = requests.patch(self.concat(link), auth=('singleuser@user.com', '123'),
			json={'first_name': 'Mario'})
		# This must be 404 NOT FOUND
		self.assertEqual(r.status_code, 404)

	def test_patch_me_change_password(self):
		""" tests to change password. It's not allowed."""
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		link = 'me/{}'.format(json_data['_id'])
		# changing
 		r = requests.patch(self.concat(link),
 			json={'password': '123'}, auth=(self.data['email'], '123')) # the owner
		self.assertEqual(r.status_code, 422)

	def test_patch_users_by_superusers(self):
		""" tests updates for users """
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		object_id = json_data['_id']
		link = 'me/{}'.format(json_data['_id'])
		# Add/Editing first_name
		self.data['first_name'] = "Mario"
 		r = requests.patch(self.concat(link),
			json=self.data, auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		self.assertEqual(r.status_code, 404)

	@unittest.skip("User cannot to edit own profile #monkeyFeature")
	def test_patch_owner(self):
		""" tests updates for users """
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Add/Editing first_name
		self.data['first_name'] = "Myself Name"
		# Editing
 		r = requests.patch(self.concat(new_user_follow_url),
 			json=self.data, auth=(self.data['email'], '123'))
		# Get to check field first_name
 		r2 = requests.get(self.concat(new_user_follow_url),
 			auth=('u@user.com', '123'))
		json_data = json.loads(r2.text)
		self.assertEqual(r.status_code, 200)
		self.assertEqual(json_data['first_name'], self.data['first_name'])

	# POST tests
	def test_post_users_by_users(self):
		""" tests if user without superusers roles can to create new user """
		# without Auth
		r = requests.post(self.concat('users'), json=self.data)
		self.assertEqual(r.status_code, 401)
		# With auto
		r = requests.post(self.concat('users'), json=self.data,
			auth=('u@user.com', '123'))
		self.assertEqual(r.status_code, 401)

	@unittest.skip(u'not defined roles')
	def test_post_users_by_admins(self):
		""" to add admin user """
		pass

	def test_post_users_by_superusers(self):
		""" tests adds an user with roles of the superusers """
		# Adding the user
		r = requests.post(self.concat('users'),
			json=self.data,
			auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		object_id = json_data['_id']
		new_user_follow_url = json_data['_links']['self']['href']
		self.assertEqual(r.status_code, 201)
		r = requests.post(self.concat('users'),
			json=self.data,
			auth=('s@super.com', '123'))
		self.assertEqual(r.status_code, 422) # It's not unique
		# check if owner is updated
		r = requests.get(self.concat(new_user_follow_url),
			auth=('u@user.com', '123'))
		json_load = json.loads(r.text)
		self.assertEqual(json_load['owner'], object_id)

	# DELETE tests
	def test_delete_users_by_users(self):
		""" trying delete an user as ordinary user """
		# Adding an user
		r = requests.post(self.concat('users'),
			json=self.data,
			auth=('s@super.com', '123'))
		# following links...
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# deleting the user as users...
		r = requests.delete(self.concat(new_user_follow_url),
			auth=('u@user.com', '123'))
		self.assertEqual(r.status_code, 401)

	def test_delete_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""
		# Adding an user
		r = requests.post(self.concat('users'),
			json=self.data,
			auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			auth=('s@super.com', '123'))
		r2 = requests.get(self.concat(new_user_follow_url),
			auth=('s@super.com', '123'))
		self.assertEqual(r.status_code, 204)
		self.assertEqual(r2.status_code, 404)

	@unittest.skip(u'SOFT_DELETE not workint')
	def test_delete_SOFT_DELETE_users_by_superusers(self):
		""" to delete by superuser with SOFT_DELETE=True"""

		# Adding an user
		r = requests.post(self.concat('users'),
			data={'email':'mmmm@mm.com', 'password': '123'},
			auth=(self.superuser.email, '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Deleting the user
		r = requests.delete(self.concat(new_user_follow_url),
			auth=(self.superuser.email, '123'))
		# Check soft delete
		u = models.User.objects.get(email=self.payload['email'])
		print u
		self.assertEqual(r.status_code, 200)

	# hooks tests
	def test_validate_email_is_not_valid(self):
		""" tests if email is not valid """
		# trying to add an user
		r = requests.post(self.concat('users'),
			json={'email':'mmmm-mmm-m3.com', 'password': '123'},
			auth=('s@super.com', '123'))
		self.assertEqual(r.status_code, 422)

	def test_set_username(self):
		""" tests if username was created correctly.
		`shortname` is deprecated. It's now `username`
		"""
		# trying to add an user
		r = requests.post(self.concat('users'), json=self.data,
			auth=('s@super.com', '123'))
		# checking data
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		r = requests.get(self.concat(new_user_follow_url),
			auth=('u@user.com', '123'))
		username_saved = json.loads(r.text)['username']
		username_sent = self.data['email'].split('@')[0].replace('.', '')
		self.assertEqual(username_sent, username_saved)

	def test_set_password_is_not_plain_text(self):
		""" tests if password is not plain text """
		# trying to add an user
		r = requests.post(self.concat('users'), json=self.data,
			auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		pk = json_data['_id']
		u = DATABASE.user.find_one({'_id': ObjectId(pk)})
		password = u['password']
		self.assertNotEqual('123', password)
		self.assertTrue(password.startswith('pbkdf2'))

	def test_md5_email(self):
		""" tests if md5_email was created """
		# trying to add an user
		r = requests.post('http://localhost:9014/api/v2/users',
			json=self.data,
			auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		r = requests.get(self.concat(new_user_follow_url),
			auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		md5_email = json_data['md5_email']
		self.assertEqual(md5_email, md5.md5(self.data['email']).hexdigest())

	@unittest.skip(u"this isn't implemented")
	def test_token_generated(self):
		pass


class IssueTestCase(ApiTests):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'marioissues_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}
		self.issue = {
			'title': 'SISCOMEX',
			'body': 'Lentidao no siscomex',
			'register': '2015RI/000{}'.format(number),
			'ugat': 'SUPOP',
			'ugser': 'SUNAF'
		}

	def test_get_issues_not_authenticated(self):
		r = requests.get(self.concat('issues'))
		self.assertEqual(r.status_code, 401)

	def test_get_issues(self):
		""" tests get issues and if is list """
		r = requests.get(self.concat('issues'), auth=('u@user.com', '123'))
		data = json.loads(r.text)
		data = data['_items']
		self.assertEqual(r.status_code, 200)
		self.assertEqual(list, type(data))

	def test_get_more_issues(self):
		"""tests get issues and if there is next the first `_items` must contain
		25 items.
		"""
		r = requests.get(self.concat('issues'), auth=('u@user.com', '123'))
		data = json.loads(r.text)
		items = data['_items']
		if 'next' in data['_links']:
			self.assertEqual(len(items), 25)
			# testing more pages
			link = data['_links']['next']['href']
			r = requests.get(self.concat(link), auth=('u@user.com', '123'))
			data = json.loads(r.text)
			items = data['_items']
			meta = data['_meta']
			self.assertEqual(list, type(items))
			self.assertEqual(meta['page'], 2)
		else:
			# this tests is possible if there is data volume or more than
			# 25 items.
			pass

	# tests of the hooks
	def test_register_normalized(self):
		""" tests if resgisters will be normalized and copy data to
		register_orig.
		"""
		# adding register
		r = requests.post(self.concat('issue'), auth=('s@super.com', '123'),
			json=self.issue)
		data = json.loads(r.text)
		link = 'issues/{}'.format(data['_id'])
		r = requests.get(self.concat(link), auth=('u@user.com', '123'))
		data = json.loads(r.text)
		self.assertNotIn('/', data['register'])
		self.assertEqual(self.issue['register'], data['register_orig'])

	def test_register_create_bulk(self):
		""" tests to create multiple items (bulk).
		"""
		number = random.randint(1, 10000)
		reg_1 = '2015RI/000{}'.format(number + 1)
		reg_2 = '2015RI/000{}'.format(number + 2)
		reg_3 = '2015RI/000{}'.format(number + 3)
		# adding register
		issues = [self.issue,
				{'title': 'Sisc1', 'body':'Fora', 'register': reg_1,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'},
				{'title': 'Sisc2', 'body':'Fora', 'register': reg_2,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'},
				{'title': 'Sisc3', 'body':'Fora', 'register': reg_3,
						'ugat': 'SUPOP', 'ugser': 'SUNAF'}
		]
		r = requests.post(self.concat('issue'), auth=('s@super.com', '123'),
			json=issues)
		data = json.loads(r.text)
		self.assertEqual(len(data['_items']), 4)

	def test_update_issue(self):
		""" tests to update issue
		"""
		# adding issue
		r = requests.post(self.concat('issue'), auth=('s@super.com', '123'),
			json=self.issue)
		data = json.loads(r.text)
		link = 'issue/{}'.format(data['_id'])
		link_i = 'issues/{}'.format(data['_id'])
		r = requests.patch(self.concat(link), auth=('s@super.com', '123'),
			json={'title': 'A new title'})
		r = requests.get(self.concat(link_i), auth=('u@user.com', '123'))
		data = json.loads(r.text)
		self.assertEqual(data['title'], 'A new title')

	def test_update_and_create_not_superusers(self):
		# TODO
		pass

	def test_slugfy(self):
		# TODO
		pass

	def test_post_save(self):
		""" tests events stream. """
		# TODO
		pass


class CommentTestCase(unittest.TestCase):

	def setUp(self):
		number = random.randint(1, 10000)
		self.data = {'email': 'marioissues_{}@mm.com'.format(number),
						'password': '123', 'roles': ["users"]}

	# tests for superusers (POST, PATCH)

	# tests for users (GET, PAGINATION)

	# tests hooks
	def test_set_shottime(self):
		pass

	def test_set_hashtags(self):
		pass

	def test_set_users_mentioned(self):
		pass

	def test_set_title(self):
		pass

	def test_post_save(self):
		pass

	def test_to_link_hashtag(self):
		pass

	def test_to_link_mention(self):
		pass

	@unittest.skip(u"This test is usefeul to webapp. The flow of the Eve skip it.")
	def test_to_json(self):
		pass

class InviteTestCase(unittest.TestCase):
	""" Invite is `yet` a case for `only` webapp. """
	pass


if __name__ == "__main__":
	unittest.main()