from flask import Flask
from flaskext.mysql import MySQL
from flask import Blueprint, request, jsonify
import json

from database import db

import MySQLdb

from common import*

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'test'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
#app.config['MYSQL_DATABASE_DB'] = 'test'

app.config['MYSQL_DATABASE_DB'] = 'perf_highload_db'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'

DB_HOST = 'localhost'
DB_USER = 'test'
DB_DATABASE = 'test'
#DB_DATABASE = 'perf_highload_db'
DB_PASSWORD = 'test'


@app.route('/db/api/clear/', methods=['POST'])
def clear():

	params = {}

	db.execute_post("DELETE Forum.* FROM Forum", params)
	db.execute_post("DELETE User.* FROM User", params)
	db.execute_post("DELETE Post.* FROM  Post", params)
	db.execute_post("DELETE Thread.* FROM  Thread", params)
	db.execute_post("DELETE Subscription.* FROM Subscription", params)
	db.execute_post("DELETE Follower.* FROM Follower", params)

	return_data  = {"code": 0, "response": "OK"}

	return jsonify (return_data)


@app.before_request
def db_connect():
	db.connection_cursor()


@app.route('/db/api/status/')
def status():

	params = {}
	
	user_count = db.execute_get("SELECT count(*) FROM User", params)
	thread_count = db.execute_get("SELECT count(*) FROM Thread", params)
	forum_count = db.execute_get("SELECT count(*) FROM Forum", params)
	post_count = db.execute_get("SELECT count(*) FROM Post", params)

	users = user_count[0][0]
	threads = thread_count[0][0]
	forums = forum_count[0][0]
	posts = post_count[0][0]

	return_data = {"code": 0, "response": {"user": users, "thread": threads, "forum": forums, "post": posts}}

	return jsonify(return_data)



##### USER 


@app.route("/db/api/user/create/", methods=["POST"])
def user_create():

	data = request.get_json()

	username = data['username']
	about = data['about']
	name = data['name']
	email = data['email']
	is_anonymous = data.get('isAnonymous', False)


	sql = """INSERT INTO User (username, about, name, email, isAnonymous) VALUES \
		(%(username)s, %(about)s, %(name)s, %(email)s, %(isAnonymous)s);"""
	params = {'username': username, 'about': about, 'name': name, 'email': email, 'isAnonymous': is_anonymous}

	try:
		my_last = db.execute_post(sql, params)

	except MySQLdb.IntegrityError, message:
		if message[0] == 1062:

			return_data = {"code": 5,"response": RESPONSE_CODE_5}

			return jsonify(return_data)

		return_data = {"code": 4,"response": RESPONSE_CODE_4}

		return jsonify(return_data)

	#user_dict = dictionary_of_user(email)

	#return_data = {"code": 0, "response": user_dict}

	response_data = {"id": my_last, "email": email, 'name': name, 'username': username, 'isAnonymous': is_anonymous, 'about': about}

	return_data = {"code": 0, "response": response_data}

	return jsonify(return_data)


@app.route("/db/api/user/details/", methods=["GET"])
def user_details():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	email = data.get('user')
	if not email:
		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	user = dictionary_of_user(email)

	params = {}
    
	sql = db.execute_get("SELECT thread FROM Subscription WHERE subscriber = '%s'" % (email), params)

	subscribed_list = list()
	for thread in sql:
		subscribed_list.append(thread[0])

	user['followers'] = followers_list(email)
	user['following'] = following_list(email)
	user['subscriptions'] = subscribed_list

	return_data = {"code": 0, "response": user}

	return jsonify(return_data)

@app.route("/db/api/user/follow/", methods=["POST"])
def follow():

	data = request.get_json()

	follower = data['follower']
	followee = data['followee']

	params = {}

	db.execute_post("INSERT INTO Follower (follower, following) VALUES ('%s','%s')" % (follower, followee), params)

	return_data = {"code": 0, "response": dictionary_of_user(follower)}

	return jsonify(return_data)


@app.route("/db/api/user/unfollow/", methods=["POST"])
def unfollow():

	data = request.get_json()

	follower = data['follower']
	followee = data['followee']

	params = {}

	db.execute_post("DELETE FROM Follower WHERE follower = '%s' AND following = '%s'" % (follower, followee), params)

	return_data = {"code": 0, "response": dictionary_of_user(follower)}

	return jsonify(return_data)

@app.route("/db/api/user/listFollowers/", methods=["GET"])
def list_followers():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	email = data.get('user')
	if not email:

		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	since_id = data.get('since_id', -1)
	if since_id != -1:

		since_sql = "AND User.user >= '%s'" % (since_id)

	else:
		since_sql = ""

	order_part = data.get('order', 'desc')

	order_sql = """ORDER BY User.name {}""".format(order_part)

	limit = data.get('limit', -1)
	if limit != -1:
		try:
			limit = int(limit)
		except ValueError:

			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify(return_data)

		if limit < 0:

			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify(return_data)

		limit_sql = "LIMIT %d" % (int(limit))

	else:
		limit_sql = ""

	sql = """SELECT about, email, user, isAnonymous, name, username FROM User JOIN Follower ON Follower.follower = User.email WHERE Follower.following"""
	sql += """ = %(email)s {since_value} {order_value} {limit_value};""".format(since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

	params = {'email': email}

	user_list_sql = db.execute_get(sql, params)


	if not user_list_sql:
		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)


	user_list = list()
	for user_sql in user_list_sql:
		follower_email = str_to_json(user_sql[1])
		user_list.append({'about': str_to_json(user_sql[0]), 'email': follower_email, 'id': str_to_json(user_sql[2]),
                          'isAnonymous': str_to_json(user_sql[3]), 'name': str_to_json(user_sql[4]), 'username': str_to_json(user_sql[5]),
                          'followers': followers_list(follower_email), 'following': following_list(follower_email), 
                          'subscriptions': get_subscribed_list(follower_email)})



	return_data = {"code": 0, "response": user_list}

	return jsonify(return_data)

@app.route("/db/api/user/listFollowing/", methods=["GET"])
def list_following():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	email = data.get('user')
	if not email:
		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	since_id = data.get('since_id', -1)
	if since_id != -1:

		since_sql = "AND User.user >= '%s'" % (since_id)
	else:
		since_sql = ""

	order_part = data.get('order', 'desc')

	order_sql = """ORDER BY User.name {}""".format(order_part)

	limit = data.get('limit', -1)
	if limit != -1:
		try:
			limit = int(limit)
		except ValueError:
			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify(return_data)

		if limit < 0:
			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify(return_data)

		limit_sql = "LIMIT %d" % (int(limit))
	else:
		limit_sql = ""

	sql = """SELECT about, email, user, isAnonymous, name, username FROM User JOIN Follower ON Follower.following = User.email WHERE Follower.follower"""
	sql += """ = %(email)s {since_value} {order_value} {limit_value};""".format(since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

	params = {'email': email}

	user_list_sql = db.execute_get(sql, params)
	
	if not user_list_sql:
		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)

	user_list = list()
	for user_sql in user_list_sql:
		follower_email = str_to_json(user_sql[1])
		user_list.append({'about': str_to_json(user_sql[0]), 'email': follower_email, 'id': str_to_json(user_sql[2]),
                          'isAnonymous': str_to_json(user_sql[3]), 'name': str_to_json(user_sql[4]), 'username': str_to_json(user_sql[5]),
                          'followers': followers_list(follower_email), 'following': following_list(follower_email),
                          'subscriptions': get_subscribed_list(follower_email)})

	return_data = {"code": 0, "response": user_list}

	return jsonify(return_data)

@app.route("/db/api/user/listPosts/", methods=["GET"])
def user_list_posts():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	email = data.get('user')
	if not email:
		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	since = data.get('since', '')
	limit = data.get('limit', -1)
	order = data.get('order', 'desc')

	post_list = get_post_list(user=email, since=since, limit=limit, order=order)

	return_data = {"code": 0, "response": post_list}

	return jsonify(return_data)


@app.route("/db/api/user/updateProfile/", methods=["POST"])
def update_profile():

	data = request.get_json()
	about = data['about']
	email = data['user']
	name = data['name']

	params = {}

	sql = "UPDATE User SET about = '%s', name = '%s' WHERE email = '%s'" % (about, name, email)

	db.execute_post(sql, params)

	return_data = {"code": 0, "response": dictionary_of_user(email)}

	return jsonify(return_data)


def followers_list(email):

	params = {}

	sql = db.execute_get("SELECT follower FROM Follower WHERE following = '%s'" % (email), params)

	if not sql:
		return list()

	return sql[0]


def following_list(email):

	params = {}

	sql = db.execute_get("SELECT following FROM Follower WHERE follower = '%s'" % (email), params)

	if not sql:
		return list()

	return sql[0]	

def get_id_thread(id_value):

    params = {}

    sql ="SELECT thread, title, user, message, forum, isDeleted, isClosed, date, slug, likes, dislikes, points, posts FROM Thread WHERE thread = '%s' LIMIT 1" % (id_value)
    
    thread_list_sql = db.execute_get(sql, params)

    if not thread_list_sql:
        return list()

    thread_sql = thread_list_sql[0]
    return {'id': str_to_json(thread_sql[0]), 'title': str_to_json(thread_sql[1]), 'user': str_to_json(thread_sql[2]),
            'message': str_to_json(thread_sql[3]), 'forum': str_to_json(thread_sql[4]), 'isDeleted': str_to_json(thread_sql[5], True),
            'isClosed': str_to_json(thread_sql[6], True), 'date': thread_sql[7].strftime('%Y-%m-%d %H:%M:%S'), 'slug': str_to_json(thread_sql[8]),
            'likes': str_to_json(thread_sql[9]), 'dislikes': str_to_json(thread_sql[10]), 'points': str_to_json(thread_sql[11]),
           	'posts': str_to_json(thread_sql[12])}

##### Forum 

@app.route("/db/api/forum/create/", methods=["POST"])
def forum_create_forum():


    data = request.get_json()

    name = data['name']
    short_name = data['short_name']
    user = data['user']

    params = {}

    sql = "INSERT INTO Forum (name, short_name, user) VALUES ('%s','%s','%s')" % (name, short_name, user)


    try:
        my_last = db.execute_post(sql,params)

    except MySQLdb.IntegrityError, message:
        print message[0]
    finally:


        forum_dict = dictionary_of_forum(short_name=short_name)

        return_data = {"code": 0, "response": forum_dict}


		# response_data = {"id": my_last, "name": name, "short_name": short_name, "user": user}

		# return_data = {"code": 0, "response": response_data}

	return jsonify(return_data)


@app.route("/db/api/forum/details/", methods=["GET"])
def forum_details():

    data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())
    
    short_name = data.get('forum')

    if not short_name:
    	return_data = {"code": 2, "response": RESPONSE_CODE_2}

    	return jsonify(return_data)

    forum_dict = dictionary_of_forum(short_name=short_name)
    if not forum_dict:
    	return_data = {"code": 1, "response": RESPONSE_CODE_1}

    	return jsonify(return_data)

    if data.get('related', '') == 'user':
        forum_dict['user'] = dictionary_of_user(forum_dict['user'])

    return_data = {"code": 0, "response": forum_dict}

    return jsonify(return_data)


@app.route("/db/api/forum/listPosts/", methods=["GET"])
def forum_list_posts():

    data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

    forum = data.get('forum')

    if not forum:
    	return_data = {"code": 2, "response": RESPONSE_CODE_2}

    	return jsonify(return_data)

    # Related part
    related_values = list()
    data_related = data.get('related')
    if type(data_related) is list:
        related_values.extend(data_related)
    elif type(data_related) is str:
        related_values.append(data_related)

    thread_related = False
    forum_related = False
    user_related = False
    for related_value in related_values:
        if related_value == 'thread':
            thread_related = True
        elif related_value == 'forum':
            forum_related = True
        elif related_value == 'user':
            user_related = True
        else:
        	return_data = {"code": 3, "response": RESPONSE_CODE_3}

        	return jsonify(return_data)

    since = data.get('since', '')
    limit = data.get('limit', -1)
    sort = data.get('sort', 'flat')
    order = data.get('order', 'desc')

    post_list = get_post_list(forum=forum, since=since, limit=limit, sort=sort, order=order)

    for post in post_list:
        if user_related:
            post['user'] = dictionary_of_user(post['user'])

        if thread_related:
            post['thread'] = get_id_thread(post['thread'])

        if forum_related:
            post['forum'] = dictionary_of_forum(short_name=post['forum'])

    return_data = {"code": 0, "response": post_list}

    return jsonify(return_data)


@app.route("/db/api/forum/listThreads/", methods=["GET"])
def forum_list_threads():

    data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

    forum = data.get('forum')

    if not forum:

        return_data = {"code": 2, "response": RESPONSE_CODE_2}

        return jsonify (return_data)

    since = data.get('since', '')
    order = data.get('order', '')
    limit = data.get('limit', -1)
    thread_list = get_thread_list(forum=forum, since=since, order=order, limit=limit)

    # Related part
    related_values = list()
    data_related = data.get('related')
    if type(data_related) is list:
        related_values.extend(data_related)
    elif type(data_related) is str:
        related_values.append(data_related)

    forum_related = False
    user_related = False
    for related_value in related_values:
        if related_value == 'forum':
            forum_related = True
        elif related_value == 'user':
            user_related = True
        else:
            return_data = {"code": 3, "response": RESPONSE_CODE_3}

            return jsonify(return_data)

    for thread in thread_list:
        if user_related:
            thread['user'] = dictionary_of_user(thread['user'])
            thread['user']['subscriptions'] = get_subscribed_list(thread['user']['email'])

        if forum_related:
            thread['forum'] = dictionary_of_forum(short_name=thread['forum'])

    return_data = {"code": 0, "response": thread_list}

    return jsonify(return_data)


@app.route("/db/api/forum/listUsers/", methods=["GET"])
def forum_list_users():

    data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

    if not data.get('forum'):
    	return_data = {"code": 2, "response": RESPONSE_CODE_2}

    	return jsonify (return_data)

    # Since id part
    since_id = data.get('since_id')
    if since_id:
        try:
            since_id = int(since_id)
        except ValueError:
        	return_data = {"code": 3, "response": RESPONSE_CODE_3}

        	return jsonify(return_data)

        since_id_sql = "AND User.user >= %d" % (since_id)

    else:
        since_id_sql = ''

    # Limit part
    if data.get('limit'):
        limit = data.get('limit')[0]
        try:
            limit = int(limit)
        except ValueError:
        	return_data = {"code": 3, "response": RESPONSE_CODE_3}

        	return jsonify(return_data)

        if limit < 0:
        	return_data = {"code": 3, "response": RESPONSE_CODE_3}

        	return jsonify(return_data)

        limit_sql = "LIMIT %d" % (int(limit))

    else:
        limit_sql = ''

    # Order part
    order_part = data.get('order', 'desc')
    order_sql = """ORDER BY User.name {}""".format(order_part)

    sql = """SELECT User.user, User.email, User.name, User.username, User.isAnonymous, User.about FROM User \
        WHERE User.email IN (SELECT DISTINCT user FROM Post WHERE forum = %(forum)s) {snc_sql} {ord_sql} \
        {lim_sql};""".format(snc_sql=since_id_sql, lim_sql=limit_sql, ord_sql=order_sql)

    params = {'forum': data.get('forum')} 

    user_list_sql = db.execute_get(sql, params)

    user_list = list()
    for user_sql in user_list_sql:
        email = str_to_json(user_sql[1])
        user_list.append({'id': str_to_json(user_sql[0]), 'email': email, 'name': str_to_json(user_sql[2]),
                          'username': str_to_json(user_sql[3]), 'isAnonymous': str_to_json(user_sql[4]),
                          'about': str_to_json(user_sql[5]), 'subscriptions': get_subscribed_list(email)})

    return_data = {"code": 0, "response": user_list}

    return jsonify(return_data)


##### Thread

@app.route("/db/api/thread/create/", methods=["POST"])
def thread_create():

	data = request.get_json()

	forum = data['forum']
	#title = encode(data.get('title'))

	title = (data.get('title').encode('utf-8'))

	is_closed  = data['isClosed']
	user = data['user']
	date = data['date']
	message = data['message']
	slug = data['slug']
	is_deleted = data.get('isDeleted', False)

	sql = """INSERT INTO Thread (forum, title, isClosed, user, date, message, slug, isDeleted) \
		VALUES (%(forum)s, %(title)s, %(isClosed)s, %(user)s, %(date)s, %(message)s, %(slug)s, %(isDeleted)s);"""
	params = {'forum': forum, 'title': title, 'isClosed': is_closed, 'user': user, 'date': date, 'message': message,
			'slug': slug, 'isDeleted': is_deleted}

	try:
		my_last = db.execute_post(sql, params)

	except MySQLdb.IntegrityError, message:
		print message[0]
	finally:

		thread_list = get_thread_list(title=title)

		if thread_list == list():
			return_data = {"code": 1, "response": RESPONSE_CODE_1}

			return jsonify(return_data)


		# response_data = {'date': date, 'forum': forum, 'id': my_last,'isClosed': is_closed, 'isDeleted': is_deleted,'message': message, 'slug': slug, 'title': title, 'user': user}

		# return_data = {"code": 0, "response": response_data}

		return_data = {"code": 0, "response": thread_list[0]}

		return jsonify(return_data)



@app.route("/db/api/thread/details/", methods=["GET"])
def thread_details():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	thread_id = data.get('thread')
	if not thread_id:
		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	thread = get_id_thread(thread_id)
	if thread == list():
		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)

	related_values = list()
	data_related = data.get('related')
	if type(data_related) is list:
		related_values.extend(data_related)
	elif type(data_related) is str:
		related_values.append(data_related)

	forum_related = False
	user_related = False
	for related_value in related_values:
		if related_value == 'forum':
			forum_related = True
		elif related_value == 'user':
			user_related = True
		else:
			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify (return_data)

	if forum_related:
		thread['forum'] = dictionary_of_forum(short_name=thread['forum'])

	if user_related:
		thread['user'] = dictionary_of_user(thread['user'])

	return_data = {"code": 0, "response": thread}

	return jsonify(return_data)

@app.route("/db/api/thread/list/", methods=["GET"])
def thread_list_method():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	if data.get('forum'):
		key = "forum"
	elif data.get('user'):
		key = "user"
	else:

		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return  jsonify(return_data) 

	key_value = data.get(key)

	since = data.get('since', '')
	order = data.get('order', '')
	limit = data.get('limit', -1)

	if key == "forum":
		thread_list = get_thread_list(forum=key_value, since=since, order=order, limit=limit)
	else:
		thread_list = get_thread_list(user=key_value, since=since, order=order, limit=limit)

	return_data = {"code": 0, "response": thread_list}

	return jsonify(return_data)


@app.route("/db/api/thread/listPosts/", methods=["GET"])
def thread_list_posts():

    data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems()) 

    thread = data.get('thread')
    since = data.get('since', '')
    limit = data.get('limit', -1)
    order = data.get('order', 'desc')
    sort = data.get('sort', 'flat')

    post_list = get_post_list(thread=thread, since=since, limit=limit, sort=sort, order=order)

    return_data = {"code": 0, "response": post_list}

    return jsonify(return_data)

@app.route("/db/api/thread/open/", methods=["POST"])
def open():
	data = request.get_json()

	thread = data['thread']

	params = {}

	db.execute_post("UPDATE Thread SET isClosed = 0 WHERE thread = '%s'" % (thread), params)

	return_data = {"code": 0, "response": thread}

	return jsonify(return_data)


@app.route("/db/api/thread/close/", methods=["POST"])
def close():
	data = request.get_json()

	thread = data['thread']

	params = {}
    
	db.execute_post("UPDATE Thread SET isClosed = 1 WHERE thread = '%s'" % (thread), params)

	return_data = {"code": 0, "response": thread}

	return jsonify(return_data)

@app.route("/db/api/thread/remove/", methods=["POST"])
def thread_remove():

    data = request.get_json()

    thread = data['thread']

    post_list = get_post_list(thread=thread)
    for post in post_list:

    	params = {}

        db.execute_post("UPDATE Post SET isDeleted = 1 WHERE post = '%s'" % (post['id']), params)

    params = {}

    db.execute_post("UPDATE Thread SET isDeleted = 1, posts = 0 WHERE thread = '%s'" % (thread), params)

    return_data = {"code": 0, "response": thread}

    return jsonify(return_data)

@app.route("/db/api/thread/restore/", methods=["POST"])
def thread_restore():
	data = request.get_json()

	thread = data['thread']

	post_list = get_post_list(thread=thread)
	for post in post_list:
		params = {}

		db.execute_post("UPDATE Post SET isDeleted = 0 WHERE post = '%s'" % (post['id']), params)

	params = {}

	db.execute_post("UPDATE Thread SET isDeleted = 0, posts = '%s' WHERE thread = '%s'" % (len(post_list), thread))

	return_data = {"code": 0, "response": thread}

	return jsonify(return_data)

@app.route("/db/api/thread/subscribe/", methods=["POST"])
def subscribe():
	data = request.get_json()

	user = data['user']
	thread = data['thread']

	try:
		params = {}

		db.execute_post("INSERT INTO Subscription (subscriber, thread) VALUES ('%s', '%s')" % (user, thread), params)

	except MySQLdb.IntegrityError, message:
		if message[0] == 1062:
			print "Already subscribed"

	result_dict = {'thread': thread, 'user': str_to_json(user)}

	return_data = {"code": 0, "response": result_dict}

	return jsonify(return_data)

@app.route("/db/api/thread/unsubscribe/", methods=["POST"])
def unsubscribe():

	data = request.get_json()

	user = data['user']
	thread = data['thread']

	params = {}

	db.execute_post("DELETE FROM Subscription WHERE subscriber = '%s' AND thread = '%s'" % (user, thread), params)

	result_dict = {'thread': thread, 'user': str_to_json(user)}

	return_data = {"code": 0, "response": result_dict}

	return jsonify(return_data)

@app.route("/db/api/thread/update/", methods=["POST"])
def thread_update():
    data = request.get_json()

    message = data['message']
    slug = data['slug']
    thread_id = data['thread']

    params = {}

    db.execute_post("UPDATE Thread SET message = '%s', slug = '%s' WHERE thread = '%s'" % (message, slug, thread_id), params)

    return_data = {"code": 0, "response": get_id_thread(thread_id)}

    return jsonify (return_data)

@app.route("/db/api/thread/vote/", methods=["POST"])
def thread_vote():
    data = request.get_json()

    vote_value = data['vote']
    thread_id = data['thread']

    if vote_value == 1:
    	params = {}

        db.execute_post("UPDATE Thread SET likes = likes + 1, points = points + 1 WHERE thread = '%s'" % (thread_id), params)

    else:
    	params = {}

        db.execute_post("UPDATE Thread SET dislikes = dislikes + 1, points = points - 1 WHERE thread = '%s'" % (thread_id), params)

    return_data = {"code": 0, "response": get_id_thread(thread_id)}

    return jsonify(return_data)


##### Post


@app.route("/db/api/post/create/", methods=["POST"])
def post_create():
	data = request.get_json()

	# Required
	date = data['date']
	thread = data['thread']
	message = data['message']
	user = data['user']
	forum = data['forum']

	# Optional
	parent = data.get('parent', None)
	is_approved = data.get('isApproved', False)
	is_highlighted = data.get('isHighlighted', False)
	is_edited = data.get('isEdited', False)
	is_spam = data.get('isSpam', False)
	is_deleted = data.get('isDeleted', False)

	try:
		sql = """INSERT INTO Post (user, thread, forum, message, parent, date, \
			isSpam, isEdited, isDeleted, isHighlighted, isApproved) VALUES \
			(%(user)s, %(thread)s, %(forum)s, %(message)s, %(parent)s, %(date)s, \
			%(isSpam)s, %(isEdited)s, %(isDeleted)s, %(isHighlighted)s, %(isApproved)s);"""

		params = {'user': user, 'thread': thread, 'forum': forum, 'message': message, 'parent': parent, 'date': date,
				'isSpam': is_spam, 'isEdited': is_edited, 'isDeleted': is_deleted, 'isHighlighted': is_highlighted,
				'isApproved': is_approved}

		post_id = db.execute_post(sql, params)
		
		post = get_id_post(post_id)

        # returnData = {"code": 0, "response": {"date": date, "forum": forum,
        #                                       "id": cursor.lastrowid, "isApproved": isApproved,
        #                                       "isEdited": isEdit, "isHighlited": isHighlighted, "isSpam": isSpam,
        #                                       "message": message, "parent": parent, "thread": thread, "user": user}}		

		response_data = {"date": date, "forum": forum,"id": post_id, "isApproved": is_approved,"isEdited": is_edited, "isHighlited": is_highlighted, "isSpam": is_spam,"message": message, "parent": parent, "thread": thread, "user": user}

		params = {}

		db.execute_post("UPDATE Thread SET posts = posts + 1 WHERE thread = '%s'" % (thread), params)
	except Exception as e:

		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)

	#return_data = {"code": 0, "response": post}

	return_data = {"code": 0, "response": response_data}

	return jsonify(return_data)



@app.route("/db/api/post/details/", methods=["GET"])
def post_details():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

	post_id = data.get('post')
	if not post_id:

		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	post = get_id_post(post_id)
	if not post:

		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)

	related_values = list()
	data_related = data.get('related')
	if type(data_related) is list:
		related_values.extend(data_related)
	elif type(data_related) is str:
		related_values.append(data_related)

	thread_related = False
	forum_related = False
	user_related = False
	for related_value in related_values:
		if related_value == 'forum':
			forum_related = True
		elif related_value == 'user':
			user_related = True
		elif related_value == 'thread':
			thread_related = True
		else:

			return_data = {"code": 3, "response": RESPONSE_CODE_3}

			return jsonify(return_data)

	if thread_related:
		post['thread'] = get_id_thread(post['thread'])

	if forum_related:
		post['forum'] = dictionary_of_forum(short_name=post['forum'])

	if user_related:
		post['user'] = dictionary_of_user(post['user'])

	return_data = {"code": 0, "response": post}

	return jsonify(return_data)


@app.route("/db/api/post/list/", methods=["GET"])
def post_list_method():

	data = dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())


	forum = data.get('forum')
	thread = data.get('thread')
	if not forum and not thread:

		return_data = {"code": 2, "response": RESPONSE_CODE_2}

		return jsonify(return_data)

	since = data.get('since', '')
	limit = data.get('limit', -1)
	order = data.get('order', '')

	if forum:
		post_list = get_post_list(forum=forum, since=since, limit=limit, order=order)
	else:
		post_list = get_post_list(thread=thread, since=since, limit=limit, order=order)

	return_data = {"code": 0, "response": post_list}

	return jsonify(return_data) 



@app.route("/db/api/post/remove/", methods=["POST"])
def post_remove():
	data = request.get_json()

	post_id = data['post']

	post = get_id_post(post_id)
	thread_id = post['thread']

	params = {}

	db.execute_post("UPDATE Post SET isDeleted = 1 WHERE post = '%s'" % (post_id), params)
	db.execute_post("UPDATE Thread SET posts = posts - 1 WHERE thread = '%s'" % (thread_id), params)	

	return_data = {"code": 0, "response": {"post": post_id}}

	return jsonify(return_data)

@app.route("/db/api/post/restore/", methods=["POST"])
def post_restore():
	data = request.get_json()

	post_id = data['post']

	post = get_id_post(post_id)
	thread_id = post['thread']

	params = {}

	db.execute_post("UPDATE Post SET isDeleted = 0 WHERE post = '%s'" % (post_id), params)
	db.execute_post("UPDATE Thread SET posts = posts + 1 WHERE thread = '%s'" % (thread_id), params)

	return_data = {"code": 0, "response": {"post": post_id}}

	return jsonify(return_data)

@app.route("/db/api/post/update/", methods=["POST"])
def post_update():
	data = request.get_json()

	post_id = data['post']

	message = data['message']

	params = {}

	db.execute_post("UPDATE Post SET message = '%s' WHERE post = '%s'" % (message, post_id),params)

	post = get_id_post(post_id)
	if not post:

		return_data = {"code": 1, "response": RESPONSE_CODE_1}

		return jsonify(return_data)

	return_data = {"code": 0, "response": post}

	return jsonify(return_data)
	

@app.route("/db/api/post/vote/", methods=["POST"])
def post_vote():

    data = request.get_json()

    post_id = data['post']
    vote_value = data['vote']

    if vote_value == 1:
    	params = {}

        db.execute_post("UPDATE Post SET likes = likes + 1, points = points + 1 WHERE post = '%s'" % (post_id), params)
    
    elif vote_value == -1:
    	params = {}

        db.execute_post("UPDATE Post SET dislikes = dislikes + 1, points = points - 1 WHERE post = '%s'" % (post_id), params)
    else:

        return_data = {"code": 3, "response": RESPONSE_CODE_3}

        return jsonify(return_data)

    post = get_id_post(post_id)
    if not post:

        return_data = {"code": 1, "response": RESPONSE_CODE_1}

        return jsonify(return_data)

    return_data = {"code": 0, "response": post}

    return jsonify(return_data)

def get_id_post(id_value):
    where_sql = "post = {}".format(id_value)


    sql = """SELECT post, user, thread, forum, message, parent, date, likes, dislikes, points, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
        WHERE post = %(id)s LIMIT 1;""".format(where_value=where_sql)

    params = {'id': id_value}

    post_list_sql = db.execute_get(sql, params)


    if not post_list_sql:
        return list()

    post_sql = post_list_sql[0]
    return {'id': str_to_json(post_sql[0]), 'user': str_to_json(post_sql[1]), 'thread': str_to_json(post_sql[2]),
            'forum': str_to_json(post_sql[3]), 'message': str_to_json(post_sql[4]), 'parent': str_to_json(post_sql[5]),
            'date': post_sql[6].strftime('%Y-%m-%d %H:%M:%S'), 'likes': str_to_json(post_sql[7]), 'dislikes': str_to_json(post_sql[8]),
            'points': str_to_json(post_sql[9]), 'isSpam': str_to_json(post_sql[10], True), 'isEdited': str_to_json(post_sql[11], True),
            'isDeleted': str_to_json(post_sql[12], True), 'isHighlighted': str_to_json(post_sql[13], True), 'isApproved': str_to_json(post_sql[14], True)}



if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run()