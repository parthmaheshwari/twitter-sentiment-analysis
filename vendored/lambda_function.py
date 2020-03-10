import imp
import os
import sys
sys.modules["sqlite"] = imp.new_module("sqlite")
sys.modules["sqlite3.dbapi2"] = imp.new_module("sqlite.dbapi2")
import json
import configparser
from textblob_pred import TwitterClient
# HERE = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(HERE, "vendor"))

"""
Declare here global objects living across requests
"""
# use Pythonic configparser to handle settings
# config = configparser.ConfigParser()
# config.read(pwd + '/settings.ini')
# instantiate the tf_model in "prediction mode"
# tf_model = Sentiment(config, is_training=False)
# just print a message so we can verify in AWS the loading of dependencies was correct
print("loaded done!")


# def validate_input(input_val):
#     try:
#         float_input = float(input_val)
#         return float_input
#     except ValueError:
#         return None


def get_param_from_url(event, param_name):
    params = event['queryStringParameters']
    return params[param_name]


def respond(code, body):
    return {"statusCode": code, "body": json.dumps(body)}


def lambda_handler(event, context):
    try:
        param = get_param_from_url(event, 'x')
        x_val = param
        api = TwitterClient()
        # calling function to get tweets
        query = x_val
        tweets = api.get_tweets(query=query, count=200)
        print(tweets)
        # picking positive tweets from tweets
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        print("Positive tweets percentage: {} %".format(
            100*len(ptweets)/len(tweets)))
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
        print("Negative tweets percentage: {} %".format(
            100*len(ntweets)/len(tweets)))
        print("Neutral tweets percentage: {} %".format(
            100*(len(tweets)-len(ptweets)-len(ntweets))/len(tweets)))

        # printing first 5 positive tweets
        ret_tweets = {
            "positive_tweets_percentage": 100*len(ptweets) / len(tweets),
            "negetive_tweets_percentage": 100*len(ntweets) / len(tweets),
            "neutral_tweets_precentage": 100*(len(tweets)-len(ptweets)-len(ntweets))/len(tweets),
            "positive_tweets": [],
            "negetive_tweets": []
        }
        for tweet in ptweets[:5]:
            ret_tweets['positive_tweets'].append(tweet)

        # printing first 5 negative tweets
        for tweet in ntweets[:5]:
            ret_tweets['negetive_tweets'].append(tweet)

        return respond(200, ret_tweets)

    except Exception as ex:
        error_response = {
            'error_message': "Unexpected error",
            'stack_trace': str(ex)
        }
        return respond(503, error_response)
