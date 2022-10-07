import sys
import imp
sys.modules["sqlite"] = imp.new_module("sqlite")
sys.modules["sqlite3.dbapi2"] = imp.new_module("sqlite.dbapi2")
# import nltk
import os
import json
import re
# import ConfigParser
"""
This is needed so that the script running on AWS will pick up the pre-compiled dependencies
from the vendored folder
"""
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(HERE, "vendored"))
"""
Now that the script knows where to look, we can safely import our objects
"""
import tweepy
from textblob import TextBlob
#import matplotlib.pyplot as plt

# event = {'queryStringParameters':{'x':'narendra modi'}}
# predict(event,'abcd')
"""
Declare here global objects living across requests
"""
# use Pythonic ConfigParser to handle settings
# Config = ConfigParser.ConfigParser()
# Config.read(HERE + '/settings.ini')

# just print a message so we can verify in AWS the loading of dependencies was correct
# print "loaded done!"


def validate_input(input_val):
    """
    Helper function to check if the input is indeed a float

    :param input_val: the value to check
    :return: the floating point number if the input is of the right type, None if it cannot be converted
    """
    try:
        float_input = float(input_val)
        return float_input
    except ValueError:
        return None


def get_param_from_url(event, param_name):
    """
    Helper function to retrieve query parameters from a Lambda call. Parameters are passed through the
    event object as a dictionary.

    :param event: the event as input in the Lambda function
    :param param_name: the name of the parameter in the query string
    :return: the parameter value
    """
    params = event['queryStringParameters']
    return params[param_name]


def return_lambda_gateway_response(code, body):
    """
    This function wraps around the endpoint responses in a uniform and Lambda-friendly way

    :param code: HTTP response code (200 for OK), must be an int
    :param body: the actual content of the response
    """
    return {"statusCode": code, "body": json.dumps(body)}

def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", tweet).split())

def get_tweets(api, query, count = 200):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
 
        try:
            # call twitter api to fetch tweets
            fetched_tweets = api.search(q = query, count = count)
 
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
 
                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                analysis = TextBlob(tweet.text)
                
                parsed_tweet['sentiment'] = analysis.sentiment.polarity
 
                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
 
            # return parsed tweets
            return tweets
 
        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def predict(event, context):
    """
    This is the function called by AWS Lambda, passing the standard parameters "event" and "context"
    When deployed, you can try it out pointing your browser to

    {LambdaURL}/{stage}/predict?x=2.7

    where {LambdaURL} is Lambda URL as returned by serveless installation and {stage} is set in the
    serverless.yml file.

    """
    try:
        param = get_param_from_url(event, 'x')
        consumer_key = ''
        consumer_secret = ''

        access_token = ''
        access_token_secret = ''

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Keyword of which sentiment to be calculated is taken from user
        # value = param

        # tweets containing keyword are collected
        # public_tweets = api.search(value)

        # list initialized to calculate total sentiments(polarity)
        total_pol = []
        k = 0

        # tweets are printed along with its individual sentiments score

        tweets = get_tweets(api,query = param, count = 200)
 
        # picking positive tweets from tweets
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] > 0]
        # percentage of positive tweets
        ptweetper = 100*len(ptweets)/len(tweets)
        # picking negative tweets from tweets
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] < 0]
        # percentage of negative tweets
        ntweetper = 100*len(ntweets)/len(tweets)
        # percentage of neutral tweets
        neutralper = 100*(len(tweets)-len(ptweets)-len(ntweets))/len(tweets)

        for tweet in tweets:
            total_pol.insert(k, tweet['sentiment'])
            k += 1
        j = 0
        n = 0
        for i in total_pol:
            j = j + i
            n = n + 1

        p = j/n
        print("Total sentiments score(-1 to 1): ", p)

    except Exception as ex:
        error_response = {
            'error_message': "Unexpected error",
            'stack_trace': str(ex)
        }
        return return_lambda_gateway_response(503, error_response)

    return return_lambda_gateway_response(200, {'Overall sentiment towards '+param: p,
    'Positive Tweets Percentage':ptweetper,'Negative Tweets Percentage':ntweetper,
    'Neutral Tweets Percentage':neutralper,'Top 5 positive tweets':ptweets[:5],
    'Top 5 negative tweets':ntweets[:5]})



