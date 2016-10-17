from slacker import Slacker
from datetime import datetime, timedelta

# this file contains models to be used for slack, which will be running through our Heroku container that the
# web site also runs on

# config #
# insert token here. right now it's just the test token
#slack = Slacker('xoxp-43417594353-43412276711-92375837862-11147d5588f674bb2a2363aee6b9ba59')
# NEED A DATA STORE TO ALLOW ABILITY TO COMPARE TO PAST PERFORMANCE


# slack functions and bots #
# color definition for communication
def define_color_communication(amount):
    if amount > 45:
        return "#23CF5F"
    if 25 < amount < 45:
        return "#FFBF00"
    else:
        return "#F64744"


# report communication metrics #
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
        'How well are we communicating on Slack over the last month?',
        attachments=[
            {
                'title': 'Last day:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d24'])) + ' messages per 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d24'])
            },
            {
                'title': 'Last 7 days:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d168'])) + ' messages per 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d168'])
            },
            {
                'title': 'Last 30 days:',
                'text': str(int(slack_summary['rolling_avg']['avg_num_messages_d720'])) + ' messages per 24 hours',
                'color': define_color_communication(slack_summary['rolling_avg']['avg_num_messages_d720'])
            }

        ],
        as_user='@communication_kpi'
    )

report_communication()

# slack bots to come #
# report site traffic
# report bank account balance
# report support tickets
# report sentiment of company


# run the slack bots daily #
def run_slack_bots():
    print('yee')

