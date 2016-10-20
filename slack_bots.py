from slacker import Slacker
from datetime import datetime, timedelta

# this file contains models in development to be used for slack, which will be running through our Heroku container
# that the web site also runs on

# config #
# insert token here. right now it's just the test token
#slack = Slacker('xoxp-43417594353-43412276711-92375837862-11147d5588f674bb2a2363aee6b9ba59')
# NEED A DATA STORE TO ALLOW ABILITY TO COMPARE TO PAST PERFORMANCE


# color definition for communication
def define_color_sentiment(amount):
    if amount >= 0.2:
        return "#23CF5F"
    elif -0.2 < amount < 0.2:
        return "#AFB9CA"
    else:
        return "#F64744"

# download nltk resources. only needed once so need to think of how to put this into production on Heroku
# import nltk
# nltk.download()


# sentiment bot #
def report_sentiment():
    # token for bot
    sentiment_kpi = Slacker('xoxb-92458687843-PTtRPnnUiGYCOjijZr0pQCXJ')
    # calculate time deltas
    d24 = (datetime.today() - timedelta(days=1)).timestamp()
    d168 = (datetime.today() - timedelta(days=7)).timestamp()
    d720 = (datetime.today() - timedelta(days=30)).timestamp()
    # get the channel ids for querying
    channel_ids = []
    channels = sentiment_kpi.channels.list().body['channels']
    for channel in channels:
        channel_ids.append(channel['id'])
    # get the information needed from all channels
    all_channels = dict()
    for channel_id in channel_ids:
        channel_summary = dict()
        channel_name = sentiment_kpi.channels.info(channel_id).body['channel']['name']
        # last 24 hours
        response_last24 = sentiment_kpi.channels.history(channel_id, oldest=d24, count=1000).body
        # last 7 days
        response_last168 = sentiment_kpi.channels.history(channel_id, oldest=d168, count=1000).body
        # last 30 days
        response_last720 = sentiment_kpi.channels.history(channel_id, oldest=d720, count=1000).body
        # assemble
        messages_24 = []
        messages_168 = []
        messages_720 = []
        for text in response_last24['messages']:
            messages_24.append(text['text'])
        for text in response_last168['messages']:
            messages_168.append(text['text'])
        for text in response_last720['messages']:
            messages_720.append(text['text'])
        # perform sentiment analysis by channel
        '''
        This tool uses the VADER (Valence Aware Dictionary and sentiment Reasoner) sentiment analysis classifier
        as published by Hutto and Gilbert in 2014. It is specifically attuned to sentiments expressed in social media,
        making it ideal for use in Slack. It is freely available for use under the MIT license.
        ------
        Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social
        Media Text. Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
        '''
        from nltk.sentiment import SentimentIntensityAnalyzer
        # import twython # needed for nltk but not specified as import?
        sid = SentimentIntensityAnalyzer()
        # create a bunch of lists for storage, probably a cleaner way to do this
        negative_scores_24 = []
        positive_scores_24 = []
        neutral_scores_24 = []
        compound_scores_24 = []
        negative_scores_168 = []
        positive_scores_168 = []
        neutral_scores_168 = []
        compound_scores_168 = []
        negative_scores_720 = []
        positive_scores_720 = []
        neutral_scores_720 = []
        compound_scores_720 = []
        for sentence in messages_24:
            ss = sid.polarity_scores(sentence)
            for k in sorted(ss):
                if k == 'compound':
                    compound_scores_24.append(ss[k])
                elif k == 'neg':
                    negative_scores_24.append(ss[k])
                elif k == 'neu':
                    neutral_scores_24.append(ss[k])
                elif k == 'pos':
                    positive_scores_24.append(ss[k])
        for sentence in messages_168:
            ss = sid.polarity_scores(sentence)
            for k in sorted(ss):
                if k == 'compound':
                    compound_scores_168.append(ss[k])
                elif k == 'neg':
                    negative_scores_168.append(ss[k])
                elif k == 'neu':
                    neutral_scores_168.append(ss[k])
                elif k == 'pos':
                    positive_scores_168.append(ss[k])
        for sentence in messages_720:
            ss = sid.polarity_scores(sentence)
            for k in sorted(ss):
                if k == 'compound':
                    compound_scores_720.append(ss[k])
                elif k == 'neg':
                    negative_scores_720.append(ss[k])
                elif k == 'neu':
                    neutral_scores_720.append(ss[k])
                elif k == 'pos':
                    positive_scores_720.append(ss[k])
        channel_summary[channel_id] = {
            'name': channel_name,
            'id': channel_id,
            'messages': {
                'messages_d24': messages_24,
                'messages_d168': messages_168,
                'messages_d720': messages_720,
            },
            'sentiment': {
                'sentiment_d24': {
                    'count_positive': len(positive_scores_24),
                    'avg_pos_score': float(sum(positive_scores_24) / (len(positive_scores_24) + 1e-5)),
                    'count_neutral': len(neutral_scores_24),
                    'avg_neu_score': float(sum(neutral_scores_24) / (len(neutral_scores_24) + 1e-5)),
                    'count_negative': len(negative_scores_24),
                    'avg_neg_score': float(sum(negative_scores_24) / (len(negative_scores_24) + 1e-5)),
                    'compound_score': float(sum(compound_scores_24) / (len(compound_scores_24) + 1e-5))
                },
                'sentiment_d168': {
                    'count_positive': len(positive_scores_168),
                    'avg_pos_score': float(sum(positive_scores_168) / (len(positive_scores_168) + 1e-5)),
                    'count_neutral': len(neutral_scores_168),
                    'avg_neu_score': float(sum(neutral_scores_168) / (len(neutral_scores_168) + 1e-5)),
                    'count_negative': len(negative_scores_168),
                    'avg_neg_score': float(sum(negative_scores_168) / (len(negative_scores_168) + 1e-5)),
                    'compound_score': float(sum(compound_scores_168) / (len(compound_scores_168) + 1e-5))
                },
                'sentiment_d720': {
                    'count_positive': len(positive_scores_720),
                    'avg_pos_score': float(sum(positive_scores_720) / (len(positive_scores_720) + 1e-5)),
                    'count_neutral': len(neutral_scores_720),
                    'avg_neu_score': float(sum(neutral_scores_720) / (len(neutral_scores_720) + 1e-5)),
                    'count_negative': len(negative_scores_720),
                    'avg_neg_score': float(sum(negative_scores_720) / (len(negative_scores_720) + 1e-5)),
                    'compound_score': float(sum(compound_scores_720) / (len(compound_scores_720) + 1e-5))
                }
            }
        }
        # store in single dict
        all_channels[channel_name] = channel_summary[channel_id]
    # summarize slack activity
    cs_24 = []
    cs_168 = []
    cs_720 = []
    slack_summary = dict()
    for channel in all_channels:
        cs_24.append(all_channels[channel]['sentiment']['sentiment_d24']['compound_score'])
        cs_168.append(all_channels[channel]['sentiment']['sentiment_d168']['compound_score'])
        cs_720.append(all_channels[channel]['sentiment']['sentiment_d720']['compound_score'])
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
                'color': define_color_sentiment(round(slack_summary['sentiment']['compound_score_24'], 1))
            },
            {
                'title': 'Last 7 days:',
                'text': str(round(slack_summary['sentiment']['compound_score_168'] * 100, 1)) + '% positive',
                'color': define_color_sentiment(round(slack_summary['sentiment']['compound_score_168'], 1))
            },
            {
                'title': 'Last 30 days:',
                'text': str(round(slack_summary['sentiment']['compound_score_720'] * 100, 1)) + '% positive',
                'color': define_color_sentiment(round(slack_summary['sentiment']['compound_score_720'], 1))
            }

        ],
        as_user='@sentiment_kpi'
    )


# report_sentiment()

# slack bots to come #
# report site traffic
# report bank account balance - this will be difficult, banks typically block access
# report support tickets

# other stuff to do #
# how to deploy sentiment bot, though?
# emoji support on sentiment (Slack, Android, iOS)
