from xero import Xero
from xero.auth import PrivateCredentials
with open('server.key') as key_file:
    rsa_key = key_file.read()
# credentials should be stored somewhere else and loaded securely, i.e. the consumer key, secret, rsa key, etc.
# current rsa key is valid until 10/28/2017 1:45:31 AM UTC
credentials = PrivateCredentials('90EDNOCOKIVDN4KGXZHTL62TFZBWBL', rsa_key)
xero = Xero(credentials)

print(xero.OBJECT_LIST)


# from slacker import Slacker
# from datetime import datetime, timedelta

# this file contains models in development to be used for slack, which will be running through our Heroku container
# that the web site also runs on

# config #
# insert token here. right now it's just the test token
# slack = Slacker('xoxp-43417594353-43412276711-92375837862-11147d5588f674bb2a2363aee6b9ba59')

