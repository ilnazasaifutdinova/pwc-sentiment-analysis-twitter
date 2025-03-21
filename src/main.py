#import libraries
from twikit import Client, TooManyRequests  #for interacting with Twitter API
import time  #for sleep functionality
from datetime import datetime  #for handling timestamps
import csv  #for writing data to CSV file
from configparser import ConfigParser  #for reading login credentials from a config file
from random import randint  #for generating random wait times


#define API credentials
api_key = 'pvumbFS1mvoBx9KkMaQpOzav4'  #twikit API key
api_secret_key = 'AfWbgkHs6wW0gtJb6qSajn2aDdDFh1yp20hZtfyLaW4Zrv8Qxt'  #twikit API secret key
access_token = '816997888492445696-mXUHka5sUJ8DZcj1HFr9bBOupXwNlzl'  #twikit access token
access_token_secret = 'z0gR6jrOsPBSrHSyiSD7gvDkXk0Tf3ANoEn3pgwv7zoVD'  #twikit access token secret
bearer_token = "AAAAAAAAAAAAAAAAAAAAAGj2uwEAAAAA80piI2AtIPWBYg%2FqpxeFnWGKafY%3Drlr26mUlUPWolnCL38aMfqxvNaMeBewnGq6AppXW6Lpn4HTjqk"  #twikit bearer token


#set the number of tweets to collect
MINIMUM_TWEETS = 200
#define the Twitter search query
QUERY = 'PwC lang:en until:2018-11-30 since:2018-11-01'

#this function retrieves tweets based on the provided query and handles rate limits.
def get_tweets(tweets):
  """

  Args:
      tweets (list, optional): A list of previously retrieved tweets (used for pagination). Defaults to None.

  Returns:
      list: A list of new tweets retrieved from the Twitter API.
  """

  if tweets is None:
    #initial tweet retrieval, get the first batch
    print(f'{datetime.now()} - Getting tweets...')
    tweets = client.search_tweet(QUERY, product='Top')
  else:
    #subsequent tweet retrieval, handle pagination and rate limits
    wait_time = randint(5, 10)  #random wait time between requests (seconds)
    print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
    time.sleep(wait_time)
    tweets = tweets.next()  #get the next page of tweets

  return tweets


#read login credentials from a configuration file "config.ini"
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']  #replace with your twikit username
email = config['X']['email']  #replace with your twikit email
password = config['X']['password']  #replace with your twikit password


#create a CSV file to store tweet data
with open('old_tweets.csv', 'w', newline='') as file:
  writer = csv.writer(file)
  writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])


#authenticate to twikit by choosing one method: login credentials or cookies
client = Client(language='en-US')

# Option 1: Login using username, email, and password (replace with your credentials)
# client.login(auth_info_1=username, auth_info_2=email, password=password)
# client.save_cookies('cookies.json')  # Save cookies for future sessions

# Option 2: Load authentication from a cookies file (requires prior login)
client.load_cookies('cookies.json')


#initialize variables for tweet count and retrieved tweets
tweet_count = 0
tweets = None

while tweet_count < MINIMUM_TWEETS:

    try:
    tweets = get_tweets(tweets)
  except TooManyRequests as e:
    #handle rate limit errors
    rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
    print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
    wait_time = rate_limit_reset - datetime.now()
    time.sleep(wait_time.total_seconds())
    continue  #continue the loop after waiting for rate limit to reset

  if not tweets:
    #no more tweets found, break the loop
    print(f'{datetime.now()} - No more tweets found')
    break

  for tweet in tweets:
    tweet_count += 1  #increment tweet count
    tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count,
                  tweet.favorite_count]  #extract tweet data

    with open('old_tweets.csv', 'a', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(tweet_data)  #append tweet data to CSV file

    print(f'{datetime.now()} - Got {tweet_count} tweets')

print(f'{datetime.now()} - Done! Got {tweet_count} tweets found')
