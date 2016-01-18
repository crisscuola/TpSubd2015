import json
import urlparse

from database import db


RESPONSE_CODE_1 = 'Requested object not found'
RESPONSE_CODE_2 = 'Invalid json'
RESPONSE_CODE_3 = 'Incorrect request'
RESPONSE_CODE_4 = 'Unknown error'
RESPONSE_CODE_5 = 'Duplicated user'


def str_to_json(value, is_bool=False):
    if is_bool:
        return value != 0

    if value == "NULL":
        return None

    return value

def dictionary_of_forum(short_name):

    params = {}

    sql =  "SELECT forum, name, short_name, user FROM Forum WHERE short_name = '%s' LIMIT 1" % (short_name)
    sql = db.execute_get(sql, params)

    if not sql:
        return dict()

    sql = sql[0]

    return {'id': str_to_json(sql[0]),'name': str_to_json(sql[1]),'short_name': str_to_json(sql[2]),'user': str_to_json(sql[3])}



def dictionary_of_user(email):

    params = {}
    
    user_list_sql = db.execute_get("SELECT user, email, name, username, isAnonymous, about FROM User WHERE email = '%s'" % (email), params)

    if not user_list_sql:
        return dict()

    sql = user_list_sql[0]

    return {'id': str_to_json(sql[0]),'email': str_to_json(sql[1]),'name': str_to_json(sql[2]),
            'username': str_to_json(sql[3]),'isAnonymous': str_to_json(sql[4], True),'about': str_to_json(sql[5])}



def get_post_list(user="", forum="", thread="", since="", limit=-1, sort='flat', order='desc'):

    if forum != "":
        where_sql = "forum = '{}'".format(forum)
    elif thread != "":
        where_sql = "thread = {}".format(thread)
    elif user != "":
        where_sql = "user = '{}'".format(user)
    else:
        return list()


    since_sql = ""
    if since != "":

        since_sql = "AND date >= '%s'" % (since) 


    if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
        return list()
    #sort_sql = """ORDER BY Post.date {}""".format(sort)
    sort_sql = """"""

 
    limit_sql = ""
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            return list()
        if limit < 0:
            return list()

        limit_sql = "LIMIT %d" % (int(limit))


    if order != 'asc' and order != 'desc':
        return json.dumps({"code": 3, "response": RESPONSE_CODE_3})
    order_sql = """ORDER BY date {}""".format(order)

    sql = "SELECT post, user, thread, forum, message, parent, date, likes, dislikes, points, \
        isSpam, isEdited, isDeleted, isHighlighted, isApproved FROM Post \
        WHERE {where_value} {since_value} {order_value} {sort_value} {limit_value}".format(
        where_value=where_sql,
        since_value=since_sql,
        limit_value=limit_sql,
        order_value=order_sql,
        sort_value=sort_sql)

    params = {}    
   
    post_list_sql = db.execute_get(sql, params)
    if not post_list_sql:
        return list()

    post_list = list()

    for post_sql in post_list_sql:
        post_list.append({'id': str_to_json(post_sql[0]), 'user': str_to_json(post_sql[1]), 'thread': str_to_json(post_sql[2]),
                          'forum': str_to_json(post_sql[3]), 'message': str_to_json(post_sql[4]), 'parent': str_to_json(post_sql[5]),
                          'date': post_sql[6].strftime('%Y-%m-%d %H:%M:%S'), 'likes': str_to_json(post_sql[7]), 'dislikes': str_to_json(post_sql[8]),
                          'points': str_to_json(post_sql[9]), 'isSpam': str_to_json(post_sql[10], True), 'isEdited': str_to_json(post_sql[11], True),
                          'isDeleted': str_to_json(post_sql[12], True), 'isHighlighted': str_to_json(post_sql[13], True), 'isApproved': str_to_json(post_sql[14], True)})

    return post_list


def get_thread_list(title="", forum="", user="", since="", limit=-1, order="desc"):
    if title != "":
        where_sql = "title = '{}'".format(title)
    elif forum != "":
        where_sql = "forum = '{}'".format(forum)
    elif user != "":
        where_sql = "user = '{}'".format(user)
    else:
        return list()


    since_sql = ""
    if since != "":
        since_sql = "AND date >= '%s'" % (since)


    if order != 'asc' and order != 'desc':
        return list()
    order_sql = """ ORDER BY date {}""".format(order)


    limit_sql = ""
    if limit != -1:
        try:
            limit = int(limit)
        except ValueError:
            return list()
        if limit < 0:
            return list()

        limit_sql = "LIMIT %d" % (int(limit))

    sql = "SELECT thread, title, user, message, forum, isDeleted, isClosed, date, slug, likes, dislikes, \
        points, posts FROM Thread WHERE {where_value} {since_value} {order_value} {limit_value}".format(
        where_value=where_sql, since_value=since_sql, order_value=order_sql, limit_value=limit_sql)

    params = {}
           
    thread_list_sql = db.execute_get(sql, params)

    if not thread_list_sql:
        return list()

    thread_list = list()

    for thread_sql in thread_list_sql:
        thread_list.append({'id': str_to_json(thread_sql[0]), 'title': str_to_json(thread_sql[1]), 'user': str_to_json(thread_sql[2]),
                            'message': str_to_json(thread_sql[3]), 'forum': str_to_json(thread_sql[4]), 'isDeleted': str_to_json(thread_sql[5], True),
                            'isClosed': str_to_json(thread_sql[6], True), 'date': thread_sql[7].strftime('%Y-%m-%d %H:%M:%S'), 'slug': str_to_json(thread_sql[8]),
                            'likes': str_to_json(thread_sql[9]), 'dislikes': str_to_json(thread_sql[10]), 'points': str_to_json(thread_sql[11]), 
                            'posts': str_to_json(thread_sql[12])})


    return thread_list

def get_params(request):
    if request.method == 'GET':
        return dict((k, v if len(v) > 1 else v[0]) for k, v in urlparse.parse_qs(request.query_string).iteritems())

    return request.json

def get_subscribed_list(email):

    params = {}
    
    sql = db.execute_get("SELECT thread FROM Subscription WHERE subscriber = '%s'" % (email), params)

    result = list()
    for thread in sql:
        result.append(thread[0])

    return result