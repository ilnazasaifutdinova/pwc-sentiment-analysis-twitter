#import libraries
import pandas as pd  #for data manipulation: Used for data manipulation and creating data structures like DataFrames
import psycopg2  #for PostgreSQL database interactions, A PostgreSQL adapter for Python, used to interact with the PostgreSQL database.
from textblob import TextBlob  #for sentiment analysis, A library for processing textual data, which includes tools for sentiment analysis.

#database connection parameters (The script named db_params)
db_params = {
    'dbname': 'dataTwitter',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

#connect to the PostgreSQL database
conn = psycopg2.connect(**db_params)  #establish a connection using the provided parameters
cur = conn.cursor()  #create a cursor (cursor object) for executing SQL queries

#fetch data from the database
cur.execute("SELECT tweet_count, username, text, created_at, retweets, likes FROM oldtweets")  #execute a query to retrieve data
rows = cur.fetchall()  #fetch all rows from the query result

#load data into a pandas DataFrame
columns = ['tweet_count', 'username', 'text', 'created_at', 'retweets', 'likes']  #define column names
df = pd.DataFrame(rows, columns=columns)  #create a pandas DataFrame from the fetched data, where DataFrame is

#perform sentiment analysis
def get_sentiment(text):
    """Calculates the sentiment polarity of a given text using TextBlob.
        The polarity is a float within the range [-1, 1], where:
            -1 indicates very negative sentiment.
            0 indicates neutral sentiment.
            1 indicates very positive sentiment.
    """
    return TextBlob(text).sentiment.polarity
    
#The get_sentiment function is applied to the text column of the DataFrame, creating a new column sentiment that contains the sentiment scores for each tweet.
df['sentiment'] = df['text'].apply(get_sentiment)  #apply the sentiment analysis function to the 'text' column. 

#update the database with sentiment analysis results
update_query = """
    UPDATE oldtweets
    SET sentiment = %s
    WHERE tweet_count = %s
"""  #define the SQL update query

for index, row in df.iterrows():  #iterate through each row in the DataFrame
    cur.execute(update_query, (row['sentiment'], row['tweet_count']))  #execute the update query with sentiment and tweet_count

#commit changes and close the connection
conn.commit()  #commit changes to the database
cur.close()  #close the database cursor
conn.close()  #close the database connection
