from slacker import Slacker
from datetime import datetime, timedelta

# this file contains models in development to be used for slack, which will be running through our Heroku container
# that the web site also runs on

# config #
# insert token here. right now it's just the test token
#slack = Slacker('xoxp-43417594353-43412276711-92375837862-11147d5588f674bb2a2363aee6b9ba59')
# NEED A DATA STORE TO ALLOW ABILITY TO COMPARE TO PAST PERFORMANCE

# slack bots to come #
# report site traffic - not convinced this is a key performance indicator for the company, though.
# report bank account balance - this will be difficult, banks typically block access
# report support tickets

# other stuff to do #
# how to deploy sentiment bot, though?
# emoji support on sentiment (Slack, Android, iOS)
