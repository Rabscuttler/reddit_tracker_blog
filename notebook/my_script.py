# My example script
import spacy
import os
import time
import praw
import pandas as pd
import numpy as np
import pprint
from datetime import datetime, timezone
from spacy import displacy
import matplotlib.pyplot as plt
from collections import Counter
import plotly.express as px
import boto3


username = "my_username"
password = "my_password"
app_client_id = "app_client_ID"
app_client_secret = "app_client_secret"
user_agent = "script:my_app:v0.1 (by u/<your_name>)"

subreddits_to_query = ["soccer", "baseball", "hockey", "mma", "running", "snowboarding",
                       "climbing", "nba", "nfl", "politics", "casualuk", "news"]

reddit = praw.Reddit(client_id=app_client_id,
                     client_secret=app_client_secret,
                     user_agent=user_agent)

# S3 storage
my_bucket_name = 'my-bucket-XXXXX'


def spacy_extract(df, label='PERSON'):
    '''
    Takes a pandas Dataframe object and a named entity label
    Returns an array of arrays for each reddit submission
    in the dataframe.
    '''
    titles = df['title']
    output = []  # output
    for title in titles:
        names = []
        title = title.replace("'s", "")  # clear out apostrophe's
        doc = nlp(title)
        for ent in doc.ents:
            if ent.label_ == label:
                names.append(ent.text)
        output.append(names)
    return output


def plot(df):
    ''' 
    Given an input dataframe plot a horizontal bar chart
    df: pandas dataframe with two columns, 'Names' and 'Count'
    look_for: string, SpaCy entity type
    subreddit: string, name of subreddit
    '''
    df = df[:20].iloc[::-1].reset_index()
    fig = px.bar(df, x="Count", y="Names", orientation='h')
    return fig


def get_subreddit(subreddit='news', look_for='PERSON', sort='top', limit=100, time_filter='month'):
    '''
    Sort can be 'top' or 'hot' or 'new'
    Limit should be max 1000
    Time_filter can be 'hour', day', 'week', 'month', 'year', 'all'
    If 'new' is selected, time_filter is unused
    '''
    if limit > 1000:
        print('Limit should be less than or equal to 1000')
        return

    time_filters = ['hour', 'day', 'week', 'month', 'year', 'all']
    if time_filter not in time_filters:
        print(f'Incorrect time filter. Expecting one of {time_filters}')

    columns = ['title', 'score', 'id', 'url', 'datetime']
    if sort == 'hot':
        df = pd.DataFrame([[x.title, x.score, x.id, x.url, datetime.fromtimestamp(x.created_utc, timezone.utc)]
                           for x in reddit.subreddit(subreddit).hot(limit=limit, time_filter=time_filter)],
                          columns=columns)
    elif sort == 'new':
        df = pd.DataFrame([[x.title, x.score, x.id, x.url, datetime.fromtimestamp(x.created_utc, timezone.utc)]
                           for x in reddit.subreddit(subreddit).new(limit=limit)],
                          columns=columns)
    else:
        df = pd.DataFrame([[x.title, x.score, x.id, x.url, datetime.fromtimestamp(x.created_utc, timezone.utc)]
                           for x in reddit.subreddit(subreddit).top(limit=limit, time_filter=time_filter)],
                          columns=columns)

    print(f'{len(df)} submissions found')
    print(f'Extracting {look_for}s')
    df['data'] = spacy_extract(df, label=look_for)

    # Return top 10
    flat_list = [item for sublist in df['data'] for item in sublist]
    c = Counter(flat_list)
    top = pd.DataFrame(c.most_common(), columns=['Names', 'Count'])

    chart = plot(top)  # plot chart
    return df, top, chart


# Save all the images locally
for subreddit in subreddits_to_query:
    df, top, chart = get_subreddit(
        subreddit=subreddit, look_for='PERSON', sort='top', limit=999, time_filter='week')
    name = f"{subreddit}.png"
    chart.write_image(name)  # save image


s3 = boto3.resource('s3')


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return


# Upload all .png files
for file in glob.glob("*.png"):
    upload_file(file, my_bucket_name)
