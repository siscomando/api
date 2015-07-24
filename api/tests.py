
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

	# PATCH tests HERE
	def test_patch_users_by_users(self):
		""" tests updates for users """
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		# Add/Editing first_name
		self.data['first_name'] = "Mario"
 		r = requests.patch(self.concat(new_user_follow_url),
 			json=self.data, auth=('u@user.com', '123')) # the owner
		self.assertEqual(r.status_code, 401)

	def test_patch_users_by_superusers(self):
		""" tests updates for users """
		# addding new user
		r = requests.post(self.concat('users'),
				json=self.data, auth=('s@super.com', '123'))
		# editing user by other user, e.g: self.user
		json_data = json.loads(r.text)
		object_id = json_data['_id']
		new_user_follow_url = json_data['_links']['self']['href']
		# Add/Editing first_name
		self.data['first_name'] = "Mario"
 		r = requests.patch(self.concat(new_user_follow_url),
			json=self.data, auth=('s@super.com', '123'))
		json_data = json.loads(r.text)
		new_user_follow_url = json_data['_links']['self']['href']
		r = requests.get(self.concat(new_user_follow_url),
			auth=('u@user.com', '123'))
		json_data = json.loads(r.text)
		self.assertEqual(json_data['first_name'], self.data['first_name'])
		self.assertEqual(object_id, json_data['owner'])
		self.assertEqual(json_data['_id'], json_data['owner'])

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


class IssueTestCase(unittest.TestCase):

	# tests of the mongoengine hooks in models
	def test_register_normalized(self):
		pass

	def test_slugfy(self):
		pass

	def test_post_save(self):
		pass


class CommentTestCase(unittest.TestCase):

	# tests of the mongoengine hooks in models
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
