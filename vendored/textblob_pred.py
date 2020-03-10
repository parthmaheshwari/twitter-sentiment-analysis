import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob


class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'BDBeOKEgCs1zf4ujhjsQ6o3jJ'
        consumer_secret = 'bGW3WJJiLSB5R3iF1QM8bXAKXkV1eLTfuMNd4YyMd1skQ4WaC9'
        access_token = '445253107-Qx4pv43hM53dPBtDVJKZePvTO9YC5lpRxcFoZqzH'
        access_token_secret = 'XJ7cleI3WiCvEiH1F4muIJebwMJaPn3rpEOAdtHTw8T8I'
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                    tweet.text)

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


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    query = input("Enter query to search :")
    tweets = api.get_tweets(query=query, count=200)
    print(tweets)
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(
        100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(
        100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(
        100*(len(tweets)-len(ptweets)-len(ntweets))/len(tweets)))

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    ret_tweets = {
        "positive_tweets_percentage": 100*len(ptweets) / len(tweets),
        "negetive_tweets_percentage": 100*len(ntweets) / len(tweets),
        "neutral_tweets_precentage": 100*(len(tweets)-len(ptweets)-len(ntweets))/len(tweets),
        "positive_tweets": [],
        "negetive_tweets": []
    }
    for tweet in ptweets[:5]:
        ret_tweets['positive_tweets'].append(tweet['text'])

    # printing first 5 negative tweets
    for tweet in ntweets[:5]:
        ret_tweets['negetive_tweets'].append(tweet['text'])

    print(ret_tweets)


if __name__ == "__main__":
    # calling main function
    main()
