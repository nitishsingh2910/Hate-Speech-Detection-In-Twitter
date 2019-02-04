from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener # With this we can listen to Tweets based on certain keywords and hashtags
from tweepy import OAuthHandler # Responsible for Authenticating for some of the authenticating credentials stored in TwitterCredentials.py file
from tweepy import Stream
import TwitterCredential
import numpy as np
import pandas as pd
from bokeh.layouts import column
from flask import request
from flask import Flask, render_template, session, redirect
app = Flask(__name__) # __name__ is just the name of the module

 
## Twitter Clients ###
class TwitterClients():
    def __init__(self,twitter_user=None):
        self.auth = TwitterAutheticator().authenticateTwitterApp()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client


    def get_user_timeline_tweets(self,num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

### Twitter Authenticator 
class TwitterAutheticator():
    def authenticateTwitterApp(self):
        auth = OAuthHandler(TwitterCredential.CONSUMER_KEY, TwitterCredential.CONSUMER_SECRET) #OAuthHandler Class which we are importing from tweepy which is responsible for authenticating code
        auth.set_access_token(TwitterCredential.ACCESS_TOKEN,TwitterCredential.ACCESS_TOKEN_SECRET);
        return auth

class TwitterStreamer():
    '''
    Class for streaming and processing live stream
    '''
    
    def __init__(self):
        self.twitter_auth = TwitterAutheticator()
    def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
        # This haldles twitter authentication and the connection to twitter connection API
        listener = TwitterListener(fetched_tweet_filename)  # Object of the class we have created
        auth = self.twitter_auth.authenticateTwitterApp()
        stream = Stream(auth,listener);
        stream.filter(track=hash_tag_list);
class TwitterListener(StreamListener):  #SthatreamListener Provides Methods We can Override that is why it is inherited
#This is basic listener class that just prints received prints to stdout
    def __init__(self,fetched_tweets_fileName):
        self.fetched_tweets_fileName = fetched_tweets_fileName
        
    def on_data(self, data):    #It is overridden method it will take data as it is getting tweets 
        try:
            print(data)
            with open(self.fetched_tweets_fileName,'a') as tf:
                tf.write((data))
            return True
        except Exception as e:
            print("Error on data: %s" %str(e))
            return True
    def on_error(self, status):
        if status == 420:
            return False
            #Returning False on_data method in case rate limit is occurs 
        print(status)

class TweetAnalyzer():
    dict = {}
#Functionalities for analyzing and categorizing content from tweets
    def tweets_to_data_frame(self,tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        return df
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')
    
    @app.route('/', methods=['POST'])
    def my_form_post():
        text = request.form['text']
        return text

    @app.route("/resultOfDict", methods=['GET','POST'])
    def resultOfDict():
        return render_template('resultOfDict.html', result = dict)
    
if __name__ == "__main__":
    app.debug = True # For Debugging Purpose Only
    twitter_client = TwitterClients()
    api = twitter_client.get_twitter_client_api()
    tweet_analyzer = TweetAnalyzer()           
    tweets = api.user_timeline(screen_name = tweet_analyzer.my_form_post(),count=10)
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    tweet_analyzer.result()