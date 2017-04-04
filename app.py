import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, redirect, abort, current_user, fresh_login_required
import flask_profiler
import hashlib
from logging import FileHandler, Formatter
from urllib.parse import urlparse
from slacker import Slacker
import os
import pymongo
import random
import requests
import time


# initialization #
# create instance of Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.update(SECRET_KEY='what_a_big_secret')
app.config["DEBUG"] = True

# create instance of Flask-Login and configure the app
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)
login_manager.login_view = 'login'

# define error logging #
basedir = os.path.abspath(os.path.dirname(__file__))
handler = FileHandler(os.path.join(basedir, 'log.txt'), encoding='utf8')
handler.setFormatter(
    Formatter('[%(asctime]s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')
)
app.logger.addHandler(handler)


# config vars #
dotenv_path = os.path.join('', '.env')
load_dotenv(dotenv_path)
mongo_url = os.getenv('MONGODB_URI')
profiler_username = os.getenv('PROFILER_USERNAME')
profiler_password = os.getenv('PROFILER_PASSWORD')
slack_lead = os.getenv('SLACK_LEAD')
slack_communication = os.getenv('SLACK_COMMUNICATION')
slack_sentiment = os.getenv('SLACK_SENTIMENT')
slack_support = os.getenv('SLACK_SUPPORT')

# app.config["flask_profiler"] = {
#     "enabled": app.config["DEBUG"],
#     "storage": {
#         "engine": "mongodb",
#         "MONGO_URL": urlparse(mongo_url[1:-1]).netloc.split(':')[1],
#         "DATABASE": "heroku_dw195pzd",
#         "COLLECTION": "measurements"
#     },
#     "basicAuth": {
#         "enabled": True,
#         "username": profiler_username,
#         "password": profiler_password
#     },
#     "ignore": [
#         "^/static/.*"
#     ]
# }


# mongo database setup #
if mongo_url:
    # mongo
    parsed = urlparse(mongo_url[1:-1])

    print(mongo_url)
    print(type(mongo_url))

    # parsed = urlsplit(mongo_url)
    db_name = parsed.path[1:]
    print(parsed)
    print(parsed.path)
    print(parsed.path[1:])
    db = pymongo.MongoClient(parsed.netloc.split(':')[1])[parsed.path[1:]]
    users = db['users']
    blog_posts = db['blog_posts']
    support_tickets = db['support_tickets']
    support_tickets = db['support_tickets']
    website_leads = db['website_leads']
    search = db['search']
    # add kpi collection
else:
    conn = pymongo.MongoClient()
    db = conn['db']
    users = db['users']
    blog_posts = db['blog_posts']
    support_tickets = db['support_tickets']
    website_leads = db['website_leads']
    search = db['search']
    # add kpi collection


# fuzzy search functionality #
# create ngrams
def make_ngrams(word, min_size, prefix_only=False):
    """
    basestring          word: word to split into ngrams
           int      min_size: minimum size of ngrams
          bool   prefix_only: Only return ngrams from start of word
    """
    length = len(word)
    size_range = range(min_size, max(length, min_size) + 1)
    if prefix_only:
        return [
            word[0:size]
            for size in size_range
        ]
    return list(set(
        word[i:i + size]
        for size in size_range
        for i in range(0, max(0, length - size) + 1)
    ))


# this function fires every time someone creates or modifies a blog post.
# n-grams are created for the title of the blog post, and used in fuzzy search
def index_for_search(title, subtitle, authors, body, external_link, external_link_name, username, url, url_new, publish_date):
    date_edited = str(datetime.utcnow())
    search.update(
        {
            'post.url': url
        },
        {
            '$set': {
                # note that for now we are only indexing off the title
                'post.title': title,
                'post.subtitle': subtitle,
                'post.authors': authors,
                'post.body': body,
                'post.external_link': external_link,
                'post.external_link_name': external_link_name,
                'post.user': username,
                'post.publish_date': publish_date,
                'post.last_edit_date': date_edited,
                'post.url': url_new,
                'post.ngrams': make_ngrams(title, min_size=2),
                "post.prefix_ngrams": u' '.join(
                    make_ngrams(title, min_size=2, prefix_only=True)
                )
            }
        },
        upsert=True
    )


# index the collection for searching
def index_collection():
    search.create_index(
        [
            ('post.ngrams', 'text'),
            ("post.prefix_ngrams", "text")
        ],
        name='search_blog_ngrams',
        weights={
            # these weights adjust how much you value the match of each search attribute
            'post.ngrams': 100,
            "post.prefix_ngrams": 200,
        }
    )


# search the collection and return the results sorted from best match to least match
def search_collection(query):
    search_result = []
    result = search.find(
        {
            '$text': {
                '$search': query
            }
        },
        {
            'post.title': True,
            'post.subtitle': True,
            'post.authors': True,
            'post.body': True,
            'post.url': True,
            'post.publish_date': True,
            'post.last_edit_date': True,
            '$score': {
                '$meta': "textScore"
            }
        }
    ).sort("score", pymongo.DESCENDING)
    for doc in result:
        search_result.append(doc)
    return search_result


# support ticket functionality #
# submit ticket
def submit_ticket(product_name, contact_name, email, phone, description, category, urgent):
    session['support_ticket_id'] = int(support_tickets.count()) + 1
    support_ticket = {
        'id': int(support_tickets.count()) + 1,
        'issue_date': str(datetime.utcnow()),
        'product_name': product_name,
        'contact_name': contact_name,
        'email': email,
        'phone': phone,
        'description': description,
        'category': category,
        'status': False,
        'urgent': urgent,
        'resolve_date': None
    }
    if support_tickets.find({'id': int(support_tickets.count()) + 1}).count() == 0:
        support_tickets.insert_one(support_ticket)
        return True
    else:
        return False


# CONFIRM TICKET THROUGH EMAIL TO USER

# resolve an open ticket
def resolve_ticket(id):
    resolve_date = str(datetime.utcnow())
    if support_tickets.find_one({'id': id}) is not None:
        support_tickets.update_one(
            {
                'id': id
            },
            {
                '$set': {
                    'status': True,
                    'resolve_date': resolve_date
                }
            }
        )
        report_ticket(id, True)
        return True
    else:
        return False


# login and logout functionality #
class User(UserMixin):
    def __init__(self, user_id):
        user = users.find_one({'username': user_id})
        self.id = user_id
        self.password = user['password']
        self.first_name = user['profile']['first_name']

    def __repr__(self):
        return '%d/%s/%s' % (self.id, self.first_name, self.password)


# create user
def create_user(firstname, lastname, email, username, password):
    user_profile = {
        'first_name': firstname,
        'last_name': lastname,
        'full_name': firstname + ' ' + lastname,
        'email': email
    }
    if users.find({'username': username}).count() == 0 and users.find({'profile.email': email}).count() == 0:
        users.insert_one({
            'username': username,
            'password': bcrypt.generate_password_hash(password),
            'profile': user_profile
        })
        return True
    else:
        return False


# remove user
def remove_user(username):
    if blog_posts.find({'post.user': username}) is not None:
        blog_posts.update_many(
            {
                'post.user': username
            },
            {
                '$set': {
                    'post.user': 'master',
                }
            }
        )
    if users.find_one({'username': username}) is not None:
        users.delete_one({'username': username})


# modify user
def modify_user(username, username_new, firstname, lastname, email):
    if blog_posts.find({'post.user': username}) is not None:
        blog_posts.update_many(
            {
                'post.user': username
            },
            {
                '$set': {
                    'post.user': username_new
                }
            }
        )
    if users.find_one({'username': username}) is not None:
        logout_user()
        users.update_one(
            {
                'username': username
            },
            {
                '$set': {
                    'username': username_new,
                    'profile.first_name': firstname,
                    'profile.last_name': lastname,
                    'profile.full_name': firstname + ' ' + lastname,
                    'profile.email': email
                }
            }
        )
        user = User(username_new)
        login_user(user)


# modify user password
def modify_user_password(username, current_password, new_password, new_password_confirm):
    user = users.find_one({'username': username})
    if bcrypt.check_password_hash(user['password'], current_password) is True and new_password == new_password_confirm:
        if users.find_one({'username': username}) is not None:
            logout_user()
            users.update_one(
                {
                    'username': username
                },
                {
                    '$set': {
                        'password': bcrypt.generate_password_hash(new_password)
                    }
                }
            )
            user = User(username)
            login_user(user)
            return True
    else:
        return False


# REPLACE WITH MAILGUN CREDENTIALS FOR REBOOT. CAN ONLY CONFIGURE ONCE WE HAVE A PERMANENT URL #
# send an email
def send_email(sender, receiver, subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/mg.valentino.io",
        auth=("api", "key-da1722fcffe7dfa9a4dced5ea076e649"),
        data={
            "from": sender,
            "to": receiver,
            "subject": subject,
            "text": text
        }
    )


# reset user password
def reset_user_password(username):
    if users.find_one(({'username': username})) is not None:
        user = users.find_one(({'username': username}))
        random_pass = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
        print(random_pass)

        users.update_one(
            {
                'username': username
            },
            {
                '$set': {
                    'password': bcrypt.generate_password_hash(random_pass)
                }
            }
        )

        # sender = "valentino.io <support@valentino.io>"
        # receiver = user['profile']['full_name'] + " <" + user['profile']['email'] + ">"
        # subject = "Your temporary password from valentino.io"
        # text = "Your temporary password is " + str(random_pass) + ". Go to valentino.io/change_password. " \
        #                                                           "Use the temporary password to login. Then use this" \
        #                                                           "temporary password, along with a new " \
        #                                                           "password of your choice, to reset your " \
        #                                                           "account password."
        # send_email(sender, receiver, subject, text)
        return True
    else:
        return False


# def send_simple_message():
#     return requests.post(
#         "https://api.mailgun.net/v3/sandboxa3c5260c4e9b42aa9dd356f221b839aa.mailgun.org/messages",
#         auth=("api", "key-da1722fcffe7dfa9a4dced5ea076e649"),
#         data={"from": "Mailgun Sandbox <postmaster@sandboxa3c5260c4e9b42aa9dd356f221b839aa.mailgun.org>",
#               "to": "Valentino Constantinou <vc1492a@gmail.com>",
#               "subject": "Hello Valentino Constantinou",
#               "text": "Congratulations Valentino Constantinou, you just sent an email with Mailgun!  You are truly "
#                       "awesome!  You can see a record of this email in your logs: https://mailgun.com/cp/log .  "
#                       "You can send up to 300 emails/day from this sandbox server.  Next, you should add your own "
#                       "domain so you can send 10,000 emails/month for free."})


### ADMIN USER OVERRIDE. WHAT THIS MEANS ACUTALLY IS TO INTEGRATE ROLES ###


# session duration
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


# blog post management #
# publish post to mongo db. all times in utc
def publish_post(title, subtitle, authors, body, username, url, publish_flag, publish_date):
    key = hashlib.sha224(str(time.time()).encode('UTF-8')).hexdigest()
    # create json-like object for the posts attributes
    post = {
        'title': title,
        'subtitle': subtitle,
        'authors': authors,
        'body': body,
        'user': username,
        # the below attribute, published, will serve as an indication for save states in the future (i.e. save not pub)
        'published': publish_flag,
        'publish_date': publish_date,
        'last_edit_date': publish_date,
        'url': url
    }
    # store the post in mongodb
    if blog_posts.find({key: {'$exists': True}}).count() == 0:
        blog_posts.insert_one({'key': key, 'post': post})
    else:
        pass


# remove post
def remove_post(url, user):
    if blog_posts.find_one({'post.url': url, 'post.user': user}) is not None:
        blog_posts.delete_one({'post.url': url, 'post.user': user})


# modify post
def modify_post(title, subtitle, authors, body, username, url, url_new):
    date_edited = str(datetime.utcnow())
    if blog_posts.find_one({'post.url': url, 'post.user': username}) is not None:
        blog_posts.update_one(
            {
                'post.url': url
            },
            {
                '$set': {
                    'post.title': title,
                    'post.subtitle': subtitle,
                    'post.authors': authors,
                    'post.body': body,
                    'post.user': username,
                    'post.last_edit_date': date_edited,
                    'post.url': url_new
                }
            }
        )


# other site functionality #
# web leads from main page
def record_web_lead(name, email, subject, message, category):
    key = hashlib.sha224(str(time.time()).encode('UTF-8')).hexdigest()
    date_posted = str(datetime.utcnow())
    post = {
        'date_posted': date_posted,
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
        'category': category
    }
    website_leads.insert_one({'key': key, 'post': post})
    return True
    # note that right now, this function always returns true.


### SAVE FOR LATER ###

### AUTOSAVE ###


# template routes #
@app.route('/', methods=['GET', 'POST'])
def home():
    posts = blog_posts.find()
    return render_template('index.html', posts=posts)


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        form = dict(request.form)
        name = form['name'][0]
        email = form['email'][0]
        # we removed the subject line from the form for now
        subject = None
        message = form['message'][0]
        category = form['category']
        if record_web_lead(name, email, subject, message, category) is True:
            render_template('contact.html',
                            message='Message sent successfully! We will be in touch as soon as possible.')
            report_lead(name, email, subject, message, category)
        else:
            render_template('contact.html',
                            message='Whoops! Please try again later.')
    return render_template('contact.html')


@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        query = request.form['query']
        ngrams = make_ngrams(query, min_size=2)
        results = search_collection(str(ngrams))
        return render_template('search.html', results=results)
    else:
        return render_template('search.html', results='')


@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        form = dict(request.form)
        print(form)
        product_name = form['product_name'][0]
        contact_name = form['contact_name'][0]
        email = form['email'][0]
        phone = form['phone'][0]
        description = form['message'][0]
        category = form['category']
        # define urgent categories
        if 'App Not Loading' in category:
            urgency = True
        else:
            urgency = False
        if submit_ticket(product_name, contact_name, email, phone, description, category, urgency) is True:
            render_template('support.html',
                            message='Message sent successfully! We will be in touch as soon as possible.')
            report_ticket(session['support_ticket_id'], False)
            # confirm_ticket() # sends out an email confirmation
        else:
            render_template('support.html',
                            message='Whoops! Please try again later.')
    return render_template('support.html')


@app.route('/support/resolve', methods=['GET', 'POST'])
@login_required
def support_resolve():
    if request.method == 'POST':
        ticket_id = int(request.form['ticket_id'])
        if resolve_ticket(ticket_id) is True:
            # confirm_ticket() # sends out an email confirmation
            return render_template('resolve.html', message='Success! The support ticket has been resolved.')
        else:
            return render_template('resolve.html', message='Ticket ID not found or invalid ID format.')
    return render_template('resolve.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    posts = blog_posts.find()
    return render_template('admin.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})
        if bcrypt.check_password_hash(user['password'], password) is True:
            id = username
            user = User(id)
            login_user(user)
            return redirect('/profile')
        else:
            return abort(401)
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')


@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        user = request.form['username']
        password = request.form['password']
        if create_user(first_name, last_name, email, user, password) is True:
            user = User(user)
            login_user(user)
            return redirect('/profile')
        else:
            error_message = 'username or email already used'
            return render_template('new_user.html', error=error_message)
    else:
        return render_template('new_user.html', error='')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    posts = blog_posts.find()
    user = current_user.get_id()
    user_profile = users.find_one({'username': user})
    return render_template('profile.html', posts=posts, user=user_profile)


@app.route('/delete_profile')
@login_required
def delete_profile():
    user = current_user.get_id()
    logout_user()
    remove_user(user)
    return redirect('/')


@app.route('/edit_profile', methods=['GET', 'POST'])
@fresh_login_required
def edit_profile():
    user = current_user.get_id()
    if users.find_one({'username': user}) is not None:
        user_profile = users.find_one({'username': user})
    if request.method == 'POST':
        user_new = request.form['username']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        modify_user(user, user_new, first_name, last_name, email)
        return redirect('/profile')

    return render_template('edit_profile.html', user=user_profile)


@app.route('/change_password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    user = current_user.get_id()
    user_profile = users.find_one({'username': user})
    if request.method == 'POST':
        current_password = request.form['currentpassword']
        new_password = request.form['newpassword']
        new_password_confirm = request.form['newpasswordconfirm']
        if modify_user_password(user, current_password, new_password, new_password_confirm) is True:
            return render_template('change_password.html', user=user_profile, message='your password has been changed')
        else:
            return render_template('change_password.html', user=user_profile, message='old password incorrect or new passwords do not match')
    return render_template('change_password.html', user=user_profile, message='')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        if reset_user_password(username) is True:
            return render_template('forgot_password.html', message='a password reset email has been sent')
        else:
            render_template('forgot_password.html', message='username not found')
    return render_template('forgot_password.html')


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    user = current_user.get_id()
    user_profile = users.find_one({'username': user})
    date_posted = str(datetime.utcnow())
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        authors = request.form['authors']
        body = request.form['body']
        user = current_user.get_id()
        url = request.form['url']
        publish_post(title, subtitle, authors, body, user, url, True, date_posted)
        index_for_search(title, subtitle, authors, body, user, '', '', url, url, date_posted)
        index_collection()
        return redirect('/profile')
    else:
        return render_template('create_post.html', user=user_profile)


@app.route('/delete_post', methods=['GET', 'POST'])
@login_required
def delete_post():
    url = session['blog_url']
    user = current_user.get_id()
    remove_post(url, user)
    return redirect('/profile')


@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    url = session['blog_url']
    user = current_user.get_id()
    user_profile = users.find_one({'username': user})
    if blog_posts.find_one({'post.url': url, 'post.user': user}) is not None:
        post = blog_posts.find_one({'post.url': url, 'post.user': user})
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        authors = request.form['authors']
        body = request.form['body']
        url_new = request.form['url']
        modify_post(title, subtitle, authors, body, user, url, url_new)
        index_for_search(title, subtitle, authors, body, user, '', '', url, url_new)
        index_collection()
        return redirect('/profile')
    else:
        return render_template('edit_post.html', post=post, user=user_profile)


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    posts = blog_posts.find()
    if request.method == 'POST':
        query = request.form['query']
        ngrams = make_ngrams(query, min_size=2)
        results = search_collection(str(ngrams))

        print(results)

        return render_template('blog.html', posts=results)
    else:
        return render_template('blog.html', posts=posts)


@app.route('/blog/<url>', methods=['GET', 'POST'])
def blog_route(url):
    url = request.path.split('/')[-1]
    post = blog_posts.find_one({'post.url': url})
    session['blog_url'] = url
    return render_template('blog_template.html', post=post)


@app.errorhandler(401)
def login_failed(e):
    return render_template('401.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


# slack functions and bots #
# color definition for communication kpi
def define_color_communication(amount):
    if amount >= 45:
        return "#23CF5F"
    elif 25 < amount < 45:
        return "#FFBF00"
    else:
        return "#F64744"


# color definition for sentiment kpi
def define_color_sentiment(amount):
    if amount >= 0.10:
        return "#23CF5F"
    elif -0.10 < amount < 0.10:
        return "#FFBF00"
    else:
        return "#F64744"


# color definition for support bot
def define_color_support_ticket(urgency):
    print(urgency)
    if urgency is True:
        return "#F64744"
    elif urgency is False:
        return "#FFBF00"
    else:
        return "#C0C0BF"


# lead bot #
def report_lead(name, email, subject, message, category):
    # token for bot
    lead_bot = Slacker(slack_lead)
    # post to slack
    lead_bot.chat.post_message(
        '#web-site',
        'New website lead from ' + name + '!',
        attachments=[
            {
                'color': '#3BBCD0',
                "fields": [
                    {
                        "title": "Contact Details",
                        "value": 'Email: ' + email,
                        "short": False
                    },
                    {
                        "title": "Topic(s)",
                        "value": ', '.join(item for item in category),
                        "short": False
                    },
                    {
                        "title": "Message",
                        "value": message,
                        "short": False
                    }
                ]
            }
        ],
        as_user='@lead_bot'
    )


# communication bot #
def report_communication():
    # token for bot
    communication_kpi = Slacker(slack_communication)
    # calculate time deltas
    d24 = (datetime.today() - timedelta(days=1)).timestamp()
    d168 = (datetime.today() - timedelta(days=7)).timestamp()
    d720 = (datetime.today() - timedelta(days=30)).timestamp()
    # get the channel ids for querying
    channel_ids = []
    channels = communication_kpi.channels.list().body['channels']
    for channel in channels:
        channel_ids.append(channel['id'])
    # get the group ids (private channels) for querying
    group_ids = []
    groups = communication_kpi.groups.list().body['groups']
    for group in groups:
        group_ids.append(group['id'])
    # get the information needed from all channels
    all_channels = dict()
    # get the information needed from all groups (private channels)
    all_groups = dict()
    for channel_id, group_id in zip(channel_ids, group_ids):
        channel_summary = dict()
        group_summary = dict()
        channel_name = communication_kpi.channels.info(channel_id).body['channel']['name']
        group_name = communication_kpi.groups.info(group_id).body['group']['name']
        # last 24 hours
        response_last24_c = communication_kpi.channels.history(channel_id, oldest=d24, count=1000).body
        response_last24_g = communication_kpi.groups.history(group_id, oldest=d24, count=1000).body
        # last 7 days
        response_last168_c = communication_kpi.channels.history(channel_id, oldest=d168, count=1000).body
        response_last168_g = communication_kpi.groups.history(group_id, oldest=d168, count=1000).body
        # last 30 days
        response_last720_c = communication_kpi.channels.history(channel_id, oldest=d720, count=1000).body
        response_last720_g = communication_kpi.groups.history(group_id, oldest=d720, count=1000).body
        # assemble
        channel_summary[channel_id] = {
            'name': channel_name,
            'id': channel_id,
            'num_messages_d24': len(response_last24_c['messages']),
            'num_messages_d168': len(response_last168_c['messages']),
            'num_messages_d720': len(response_last720_c['messages'])
        }
        group_summary[group_id] = {
            'name': group_name,
            'id': group_id,
            'num_messages_d24': len(response_last24_g['messages']),
            'num_messages_d168': len(response_last168_g['messages']),
            'num_messages_d720': len(response_last720_g['messages']),
        }
        # store in single dict
        all_channels[channel_name] = channel_summary[channel_id]
        all_groups[group_name] = group_summary[group_id]
    # summarize slack activity
    num_24 = []
    num_168 = []
    num_720 = []
    slack_summary = dict()
    for channel, group in zip(all_channels, all_groups):
        num_24.append(all_channels[channel]['num_messages_d24'])
        num_24.append(all_groups[group]['num_messages_d24'])
        num_168.append(all_channels[channel]['num_messages_d168'])
        num_168.append(all_groups[group]['num_messages_d168'])
        num_720.append(all_channels[channel]['num_messages_d720'])
        num_720.append(all_groups[group]['num_messages_d720'])

    slack_summary['rolling_avg'] = {
        'avg_num_messages_d24': sum(num_24),
        'avg_num_messages_d168': (sum(num_168) / 7),
        'avg_num_messages_d720': (sum(num_720) / 30)
    }
    # post to slack
    communication_kpi.chat.post_message(
        '#kpi',
        'How often are we communicating?',
        attachments=[
            {
                'title': 'Last day:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d24'])) + ' messages in 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d24'])
            },
            {
                'title': 'Last 7 days:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d168'])) + ' messages every 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d168'])
            },
            {
                'title': 'Last 30 days:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d720'])) + ' messages every 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d720'])
            }

        ],
        as_user='@communication_kpi'
    )


# sentiment bot #
def report_sentiment():
    # token for bot
    sentiment_kpi = Slacker(slack_sentiment)
    # calculate time deltas
    d24 = (datetime.today() - timedelta(days=1)).timestamp()
    d168 = (datetime.today() - timedelta(days=7)).timestamp()
    d720 = (datetime.today() - timedelta(days=30)).timestamp()
    # get the channel ids for querying
    channel_ids = []
    channels = sentiment_kpi.channels.list().body['channels']
    # get the group ids (private channels) for querying
    group_ids = []
    groups = sentiment_kpi.groups.list().body['groups']
    for channel, group in zip(channels, groups):
        channel_ids.append(channel['id'])
        group_ids.append(group['id'])
    # get the information needed from all channels and groups
    all_channels = dict()
    all_groups = dict()
    # iterate
    for channel_id, group_id in zip(channel_ids, group_ids):
        channel_summary = dict()
        group_summary = dict()
        channel_name = sentiment_kpi.channels.info(channel_id).body['channel']['name']
        group_name = sentiment_kpi.groups.info(group_id).body['group']['name']
        # last 24 hours
        response_last24_c = sentiment_kpi.channels.history(channel_id, oldest=d24, count=1000).body
        response_last24_g = sentiment_kpi.groups.history(group_id, oldest=d24, count=1000).body
        # last 7 days
        response_last168_c = sentiment_kpi.channels.history(channel_id, oldest=d168, count=1000).body
        response_last168_g = sentiment_kpi.groups.history(group_id, oldest=d168, count=1000).body
        # last 30 days
        response_last720_c = sentiment_kpi.channels.history(channel_id, oldest=d720, count=1000).body
        response_last720_g = sentiment_kpi.groups.history(group_id, oldest=d720, count=1000).body
        # assemble
        messages_24_c = []
        messages_24_g = []
        messages_168_c = []
        messages_168_g = []
        messages_720_c = []
        messages_720_g = []
        # we want to filter each message for stop words and remove them
        from nltk.corpus import stopwords
        for text_c, text_g in zip(response_last24_c['messages'], response_last24_g['messages']):
            messages_24_c.append(
                ' '.join(token for token in text_c['text'].split(' ') if token not in stopwords.words('english')))
            messages_24_g.append(
                ' '.join(token for token in text_g['text'].split(' ') if token not in stopwords.words('english')))
        for text_c, text_g in zip(response_last168_c['messages'], response_last168_g['messages']):
            messages_168_c.append(
                ' '.join(token for token in text_c['text'].split(' ') if token not in stopwords.words('english')))
            messages_168_g.append(
                ' '.join(token for token in text_g['text'].split(' ') if token not in stopwords.words('english')))
        for text_c, text_g in zip(response_last720_c['messages'], response_last720_g['messages']):
            messages_720_c.append(
                ' '.join(token for token in text_c['text'].split(' ') if token not in stopwords.words('english')))
            messages_720_g.append(
                ' '.join(token for token in text_g['text'].split(' ') if token not in stopwords.words('english')))
        # perform sentiment analysis by channel
        '''
        This tool uses the VADER (Valence Aware Dictionary and sentiment Reasoner) sentiment analysis classifier
        as published by Hutto and Gilbert in 2014. It is specifically attuned to sentiments expressed in social media,
        making it ideal for use in Slack. It is freely available for use under the MIT license.
        ------
        Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social
        Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
        ------
        NLTK on Heroku: https://stackoverflow.com/questions/13965823/resource-corpora-wordnet-not-found-on-heroku/14869451#14869451
        ------
        Nevertheless, it is probably prudent to explore other sentiment analyzers to compare performance.
        '''
        from nltk.sentiment import SentimentIntensityAnalyzer
        from nltk import data as nltk_data
        nltk_data.path.append('static/data/nltk')
        # import twython # needed for nltk but not specified as import?
        sid = SentimentIntensityAnalyzer()
        # create a bunch of lists for storage, probably a cleaner way to do this
        negative_scores_24_c = []
        negative_scores_24_g = []
        positive_scores_24_c = []
        positive_scores_24_g = []
        neutral_scores_24_c = []
        neutral_scores_24_g = []
        compound_scores_24_c = []
        compound_scores_24_g = []
        negative_scores_168_c= []
        negative_scores_168_g = []
        positive_scores_168_c = []
        positive_scores_168_g = []
        neutral_scores_168_c = []
        neutral_scores_168_g = []
        compound_scores_168_c = []
        compound_scores_168_g = []
        negative_scores_720_c = []
        negative_scores_720_g = []
        positive_scores_720_c = []
        positive_scores_720_g = []
        neutral_scores_720_c = []
        neutral_scores_720_g = []
        compound_scores_720_c = []
        compound_scores_720_g = []
        # iterate through the sentences, score them, and store the resulting score
        for sentence_c, sentence_g in zip(messages_24_c, messages_24_g):
            ss_c = sid.polarity_scores(sentence_c)
            ss_g = sid.polarity_scores(sentence_g)
            compound_scores_24_c.append(ss_c['compound'])
            compound_scores_24_g.append(ss_g['compound'])
            negative_scores_24_c.append(ss_c['neg'])
            negative_scores_24_g.append(ss_g['neg'])
            positive_scores_24_c.append(ss_c['pos'])
            positive_scores_24_g.append(ss_g['pos'])
            neutral_scores_24_c.append(ss_c['neu'])
            neutral_scores_24_g.append(ss_g['neu'])
        for sentence_c, sentence_g in zip(messages_168_c, messages_168_g):
            ss_c = sid.polarity_scores(sentence_c)
            ss_g = sid.polarity_scores(sentence_g)
            compound_scores_168_c.append(ss_c['compound'])
            compound_scores_168_g.append(ss_g['compound'])
            negative_scores_168_c.append(ss_c['neg'])
            negative_scores_168_g.append(ss_g['neg'])
            positive_scores_168_c.append(ss_c['pos'])
            positive_scores_168_g.append(ss_g['pos'])
            neutral_scores_168_c.append(ss_c['neu'])
            neutral_scores_168_g.append(ss_g['neu'])
        for sentence_c, sentence_g in zip(messages_720_c, messages_720_g):
            ss_c = sid.polarity_scores(sentence_c)
            ss_g = sid.polarity_scores(sentence_g)
            compound_scores_720_c.append(ss_c['compound'])
            compound_scores_720_g.append(ss_g['compound'])
            negative_scores_720_c.append(ss_c['neg'])
            negative_scores_720_g.append(ss_g['neg'])
            positive_scores_720_c.append(ss_c['pos'])
            positive_scores_720_g.append(ss_g['pos'])
            neutral_scores_720_c.append(ss_c['neu'])
            neutral_scores_720_g.append(ss_g['neu'])
        # channels
        channel_summary[channel_id] = {
            'name': channel_name,
            'id': channel_id,
            'messages': {
                'messages_d24': messages_24_c,
                'messages_d168': messages_168_c,
                'messages_d720': messages_720_c,
            },
            'sentiment': {
                'sentiment_d24': {
                    'count_positive': len(positive_scores_24_c),
                    'avg_pos_score': float(sum(positive_scores_24_c) / (len(positive_scores_24_c) + 1e-5)),
                    'count_neutral': len(neutral_scores_24_c),
                    'avg_neu_score': float(sum(neutral_scores_24_c) / (len(neutral_scores_24_c) + 1e-5)),
                    'count_negative': len(negative_scores_24_c),
                    'avg_neg_score': float(sum(negative_scores_24_c) / (len(negative_scores_24_c) + 1e-5)),
                    'compound_score': float(sum(compound_scores_24_c) / (len(compound_scores_24_c) + 1e-5))
                },
                'sentiment_d168': {
                    'count_positive': len(positive_scores_168_c),
                    'avg_pos_score': float(sum(positive_scores_168_c) / (len(positive_scores_168_c) + 1e-5)),
                    'count_neutral': len(neutral_scores_168_c),
                    'avg_neu_score': float(sum(neutral_scores_168_c) / (len(neutral_scores_168_c) + 1e-5)),
                    'count_negative': len(negative_scores_168_c),
                    'avg_neg_score': float(sum(negative_scores_168_c) / (len(negative_scores_168_c) + 1e-5)),
                    'compound_score': float(sum(compound_scores_168_c) / (len(compound_scores_168_c) + 1e-5))
                },
                'sentiment_d720': {
                    'count_positive': len(positive_scores_720_c),
                    'avg_pos_score': float(sum(positive_scores_720_c) / (len(positive_scores_720_c) + 1e-5)),
                    'count_neutral': len(neutral_scores_720_c),
                    'avg_neu_score': float(sum(neutral_scores_720_c) / (len(neutral_scores_720_c) + 1e-5)),
                    'count_negative': len(negative_scores_720_c),
                    'avg_neg_score': float(sum(negative_scores_720_c) / (len(negative_scores_720_c) + 1e-5)),
                    'compound_score': float(sum(compound_scores_720_c) / (len(compound_scores_720_c) + 1e-5))
                }
            }
        }
        # store in single dict
        all_channels[channel_name] = channel_summary[channel_id]
        # groups
        group_summary[group_id] = {
            'name': group_name,
            'id': group_id,
            'messages': {
                'messages_d24': messages_24_g,
                'messages_d168': messages_168_g,
                'messages_d720': messages_720_g,
            },
            'sentiment': {
                'sentiment_d24': {
                    'count_positive': len(positive_scores_24_g),
                    'avg_pos_score': float(sum(positive_scores_24_g) / (len(positive_scores_24_g) + 1e-5)),
                    'count_neutral': len(neutral_scores_24_g),
                    'avg_neu_score': float(sum(neutral_scores_24_g) / (len(neutral_scores_24_g) + 1e-5)),
                    'count_negative': len(negative_scores_24_g),
                    'avg_neg_score': float(sum(negative_scores_24_g) / (len(negative_scores_24_g) + 1e-5)),
                    'compound_score': float(sum(compound_scores_24_g) / (len(compound_scores_24_g) + 1e-5))
                },
                'sentiment_d168': {
                    'count_positive': len(positive_scores_168_g),
                    'avg_pos_score': float(sum(positive_scores_168_g) / (len(positive_scores_168_g) + 1e-5)),
                    'count_neutral': len(neutral_scores_168_g),
                    'avg_neu_score': float(sum(neutral_scores_168_g) / (len(neutral_scores_168_g) + 1e-5)),
                    'count_negative': len(negative_scores_168_g),
                    'avg_neg_score': float(sum(negative_scores_168_g) / (len(negative_scores_168_g) + 1e-5)),
                    'compound_score': float(sum(compound_scores_168_g) / (len(compound_scores_168_g) + 1e-5))
                },
                'sentiment_d720': {
                    'count_positive': len(positive_scores_720_g),
                    'avg_pos_score': float(sum(positive_scores_720_g) / (len(positive_scores_720_g) + 1e-5)),
                    'count_neutral': len(neutral_scores_720_g),
                    'avg_neu_score': float(sum(neutral_scores_720_g) / (len(neutral_scores_720_g) + 1e-5)),
                    'count_negative': len(negative_scores_720_g),
                    'avg_neg_score': float(sum(negative_scores_720_g) / (len(negative_scores_720_g) + 1e-5)),
                    'compound_score': float(sum(compound_scores_720_g) / (len(compound_scores_720_g) + 1e-5))
                }
            }
        }
        # store in single dict
        all_groups[group_name] = group_summary[group_id]
    # summarize slack activity
    cs_24 = []
    cs_168 = []
    cs_720 = []
    slack_summary = dict()
    for channel, group in zip(all_channels, all_groups):
        cs_24.append(all_channels[channel]['sentiment']['sentiment_d24']['compound_score'])
        cs_24.append(all_groups[group]['sentiment']['sentiment_d24']['compound_score'])
        cs_168.append(all_channels[channel]['sentiment']['sentiment_d168']['compound_score'])
        cs_168.append(all_groups[group]['sentiment']['sentiment_d168']['compound_score'])
        cs_720.append(all_channels[channel]['sentiment']['sentiment_d720']['compound_score'])
        cs_720.append(all_groups[group]['sentiment']['sentiment_d720']['compound_score'])
    slack_summary['sentiment'] = {
        'compound_score_24': sum(cs_24) / len(cs_24),
        'compound_score_168': sum(cs_168) / len(cs_168),
        'compound_score_720': sum(cs_720) / len(cs_720),
        'channels': all_channels
    }
    # post to slack
    sentiment_kpi.chat.post_message(
        '#kpi',
        'How are we feeling?',
        attachments=[
            {
                'title': 'Last day:',
                'text': str(round(slack_summary['sentiment']['compound_score_24'] * 100, 1)) + '% positive',
                'color': define_color_sentiment(slack_summary['sentiment']['compound_score_24'])
            },
            {
                'title': 'Last 7 days:',
                'text': str(round(slack_summary['sentiment']['compound_score_168'] * 100, 1)) + '% positive',
                'color': define_color_sentiment(slack_summary['sentiment']['compound_score_168'])
            },
            {
                'title': 'Last 30 days:',
                'text': str(round(slack_summary['sentiment']['compound_score_720'] * 100, 1)) + '% positive',
                'color': define_color_sentiment(slack_summary['sentiment']['compound_score_720'])
            }

        ],
        as_user='@sentiment_kpi'
    )


# support bot
def report_ticket(id, resolve):
    # token for bot
    support_helper = Slacker(slack_support)
    ticket = support_tickets.find_one({'id': id})
    # post to slack
    if resolve is False:
        support_helper.chat.post_message(
            '#support',
            'Support ticket #' + str(id) + ' has been issued. To resolve, visit /support/resolve.',
            attachments=[
                {
                    'title': ticket['contact_name'] + ' at ' + ticket['product_name'],
                    'text': ticket['description'],
                    'fields': [
                        {
                            "title": "Topic(s)",
                            "value": ', '.join(item for item in ticket['category']),
                            "short": False
                        },
                        {
                            "title": "Email",
                            "value": ticket['email'],
                            "short": True
                        },
                        {
                            "title": "Phone",
                            "value": ticket['phone'],
                            "short": True
                        }
                    ],
                    'color': define_color_support_ticket(ticket['urgent'])
                },
            ],
            as_user='@support_bot'
        )
    elif resolve is True:
        forms_of_gratitude = ['Thanks, guys!', 'Cool support system.', 'That was fast!']
        support_helper.chat.post_message(
            '#support',
            'Support ticket #' + str(id) + ' has been resolved!',
            attachments=[
                {
                    'title': ticket['contact_name'] + ': "' + random.choice(forms_of_gratitude) + '"',
                    'fields': [
                        {
                            "title": "Email",
                            "value": ticket['email'],
                            "short": True
                        },
                        {
                            "title": "Phone",
                            "value": ticket['phone'],
                            "short": True
                        }
                    ],
                    'color': "#23CF5F"
                },
            ],
            as_user='@support_bot'
        )


# cron scheduler for functions that fire periodically, like Slack bots #
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    report_communication,
    'interval',
    minutes=1440
)
scheduler.add_job(
    report_sentiment,
    'interval',
    minutes=1440
)
# shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# run the Flask app #
# flask_profiler.init_app(app)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
