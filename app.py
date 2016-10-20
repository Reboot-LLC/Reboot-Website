from flask import Flask, render_template, request, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, redirect, abort, current_user, fresh_login_required
from logging import FileHandler, Formatter
from datetime import timedelta, datetime
from urllib.parse import urlsplit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from slacker import Slacker
import pymongo
import os
import hashlib
import time
import random
import requests
import atexit

# initialization #
# create instance of Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.update(SECRET_KEY='what_a_big_secret')

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

# mongo database setup #
mongo_url = os.getenv('MONGOLAB_URI', 'mongodb://heroku_dw195pzd:71cjfem949up0gml4pkpe0r9r@ds011775.mlab.com:11775/heroku_dw195pzd')
if mongo_url:
    parsed = urlsplit(mongo_url)
    db_name = parsed.path[1:]
    db = pymongo.MongoClient(mongo_url)[db_name]
    users = db['users']
    blog_posts = db['blog_posts']
else:
    conn = pymongo.MongoClient()
    db = conn['db']
    users = db['users']
    blog_posts = db['blog_posts']

# for local testing #
# test = blog_posts.find()
# for i in test:
#     print(i)
#
# test = users.find()
# for i in test:
#     print(i)


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
def publish_post(title, subtitle, authors, body, username, url, publish_flag):
    key = hashlib.sha224(str(time.time()).encode('UTF-8')).hexdigest()
    date_posted = str(datetime.utcnow())
    # create json-like object for the posts attributes
    post = {
        'title': title,
        'subtitle': subtitle,
        'authors': authors,
        'body': body,
        'user': username,
        # the below attribute, published, will serve as an indication for save states in the future (i.e. save not pub)
        'published': publish_flag,
        'publish_date': date_posted,
        'last_edit_date': date_posted,
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


### SAVE FOR LATER ###

### AUTOSAVE ###


# template routes #
@app.route('/', methods=['GET', 'POST'])
def home():
    posts = blog_posts.find()
    return render_template('index.html', posts=posts)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    posts = blog_posts.find()
    return render_template('admin.html', posts=posts)


@app.route('/portfolio/datadrivenmarathon')
def datadrivenmarathon():
    return render_template('portfolio/datadrivenmarathon.html')


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
    if request.method == 'POST':
        current_password = request.form['currentpassword']
        new_password = request.form['newpassword']
        new_password_confirm = request.form['newpasswordconfirm']
        if modify_user_password(user, current_password, new_password, new_password_confirm) is True:
            return render_template('change_password.html', user=user, message='your password has been changed')
        else:
            return render_template('change_password.html', user=user, message='old password incorrect or new passwords do not match')
    return render_template('change_password.html', user=user, message='')


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
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        authors = request.form['authors']
        body = request.form['body']
        user = current_user.get_id()
        url = request.form['url']
        publish_post(title, subtitle, authors, body, user, url, True)
        return redirect('/profile')
    else:
        return render_template('create_post.html')


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
    if blog_posts.find_one({'post.url': url, 'post.user': user}) is not None:
        post = blog_posts.find_one({'post.url': url, 'post.user': user})
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        authors = request.form['authors']
        body = request.form['body']
        url_new = request.form['url']
        modify_post(title, subtitle, authors, body, user, url, url_new)
        return redirect('/profile')
    else:
        return render_template('edit_post.html', post=post)


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
# color definition for communication
def define_color_communication(amount):
    if amount >= 45:
        return "#23CF5F"
    elif 25 < amount < 45:
        return "#FFBF00"
    else:
        return "#F64744"


# communication bot #
def report_communication():
    # token for bot
    communication_kpi = Slacker('xoxb-92491297476-u4yNkWPlqApD9RWn5eLQJt1C')
    # calculate time deltas
    d24 = (datetime.today() - timedelta(days=1)).timestamp()
    d168 = (datetime.today() - timedelta(days=7)).timestamp()
    d720 = (datetime.today() - timedelta(days=30)).timestamp()
    # get the channel ids for querying
    channel_ids = []
    channels = communication_kpi.channels.list().body['channels']
    for channel in channels:
        channel_ids.append(channel['id'])
    # get the information needed from all channels
    all_channels = dict()
    for channel_id in channel_ids:
        channel_summary = dict()
        channel_name = communication_kpi.channels.info(channel_id).body['channel']['name']
        # last 24 hours
        response_last24 = communication_kpi.channels.history(channel_id, oldest=d24, count=1000).body
        # last 7 days
        response_last168 = communication_kpi.channels.history(channel_id, oldest=d168, count=1000).body
        # last 30 days
        response_last720 = communication_kpi.channels.history(channel_id, oldest=d720, count=1000).body
        # assemble
        channel_summary[channel_id] = {
            'name': channel_name,
            'id': channel_id,
            'num_messages_d24': len(response_last24['messages']),
            'num_messages_d168': len(response_last168['messages']),
            'num_messages_d720': len(response_last720['messages'])
        }
        # store in single dict
        all_channels[channel_name] = channel_summary[channel_id]
    # summarize slack activity
    num_24 = []
    num_168 = []
    num_720 = []
    slack_summary = dict()
    for channel in all_channels:
        num_24.append(all_channels[channel]['num_messages_d24'])
        num_168.append(all_channels[channel]['num_messages_d168'])
        num_720.append(all_channels[channel]['num_messages_d720'])
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


# cron scheduler for functions that fire periodically, like Slack bots #
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=report_communication,
#     trigger=IntervalTrigger(days=1)
# )
# # shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())


# run the Flask app #
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
