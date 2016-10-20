**Reboot, LLC Website**

The Reboot, LLC website with user login and profiles, and blog post 
functionality. Built with Flask and MongoDB on top of Python 3.5.1. 

Non-native python dependencies:
* pymongo
* flask
* flask-login
* flask-bcrypt
* requests
* cffi
* slacker
* APScheduler
* twython
* nltk

Some features to add: 
* login roles (i.e. admin, normal user, team leader, etc.)
* refresh token on password refresh
* set up Mailgun account for emailing password resets and such
* nice front end features like "this username is taken" without submit
* more Slack KPIs (see slack_bots.py for bots in development)