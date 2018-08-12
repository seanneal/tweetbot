'''
First Version: Tweets contents from subreddits
'''
import time
import configparser
from collections import namedtuple
import praw
import tweepy

# defines our interface with reddit post model.
Post = namedtuple('Post',
                  ['id',
                   'title',
                   'url',
                   'reddit_url',
                   'domain',
                   'user',
                   'subreddit_name',
                   'is_self',
                   'stickied'])

# subreddits we're going to use.
source_subreddits = {
    'ethereum',
    'btc',
    'bitcoin',
    'dataengineering',
    'datascience',
    'Monero',
    'dailyverse',
    'dataisugly',
    'ProgrammerHumor',
    'seahawks',
    'cowboys',
    'SeattleWa'}


def strip_title(title, max_len):
    '''
    shortens title to fit in the tweet
    '''
    if len(title) <= max_len:
        return title
    else:
        return title[:max_len - 3] + "..."


def get_posts(reddit_connection, subreddit_name):
    '''
    grabs posts from reddit and formats them for processing
    '''
    posts = []
    print('[bot] Getting posts from Reddit\\r\\{}'.format(subreddit_name))
    subreddit = reddit_connection.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=10):
        post = Post(id=submission.id,
                    title=submission.title,
                    url=submission.url,
                    reddit_url=submission.shortlink,
                    domain=submission.domain,
                    user=submission.author.name,
                    subreddit_name=submission.subreddit.display_name,
                    is_self=submission.is_self,
                    stickied=submission.stickied
                    )
        posts.append(post)
    return posts


def setup_reddit_connection():
    '''
    Gets a connection to the subreddit.
    uses the config in praw.ini  needs to be in working directory
    see: http://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
    '''
    print('[bot1] setting up connection with Reddit')
    return praw.Reddit('bot1', user_agent='bot1 user agent')


def duplicate_check(post_id):
    '''
    Checks the 'db' to see if this has already been posted
    '''
    with open('posted_posts.txt', 'r') as file:
        for line in file:
            if post_id in line:
                return True
    return False


def add_id_to_file(post_id):
    '''
    adds an entry to the 'db' to track what has been posted
    '''
    with open('posted_posts.txt', 'a') as file:
        file.write(str(post_id) + "\n")


def filter_posts(posts):
    '''
    filters the posts
    '''
    filtered_domains = {'imgur.com'}

    should_be_filtered = \
        lambda post: post.domain in filtered_domains or \
        duplicate_check(post.id) or \
        post.stickied

    return (x for x in posts if not should_be_filtered(x))


def convert_post_to_tweet(post):
    '''
    split the post into two tweets, one primary and one that is the reply.
    keep all the communication here.
    '''
    user_preamble = 'u/{user} says: '.format(user=post.user)
    # use 138 to reserve spaces to split url, hashtags and title
    hash_tag = '#{tag}'.format(tag=post.subreddit_name)
    shortened_title = strip_title(
        post.title, 138 - 23 - len(user_preamble) - len(hash_tag))
    primary_tweet = user_preamble + shortened_title + ' ' + post.url + ' ' + hash_tag
    reply_tweet = ''
    if not post.is_self:
        reply_tweet = 'further discussion to be had here: {url}'.format(
            url=post.reddit_url)
    return primary_tweet, reply_tweet


def tweeter(posts):
    '''
    puts the posts on twitter
    '''
    config = read_config()
    auth = tweepy.OAuthHandler(
        config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'],
                          config['access_token_secret'])
    api = tweepy.API(auth)
    for post in filter_posts(posts):
        print('[bot] Posting these tweets')
        primary_tweet, reply_tweet = convert_post_to_tweet(post)
        print('\t' + primary_tweet)
        print('\t\t' + reply_tweet)
        try:
            first_tweet_status = api.update_status(primary_tweet)
            if '' != reply_tweet:
                api.update_status(reply_tweet, first_tweet_status.id)
        except Exception as e:
            print(e)
        add_id_to_file(post.id)
        time.sleep(62)


def read_config():
    '''
    reads from 'tweepy.ini' which must be in the working directory
    '''
    config = configparser.ConfigParser()
    config.read('tweepy.ini')
    return {key: config['bot1'][key] for key in config['bot1']}


def write_config(config_dict):
    '''
    write 'tweepy.ini' with updated values
    '''
    config = configparser.ConfigParser()
    config.read('tweepy.ini')
    for key in config_dict:
        config['bot1'][key] = config_dict[key]
    with open('tweepy.ini', 'w') as configfile:
        config.write(configfile)


def refresh_access_token():
    '''
    interactive function that gets the access token and access token secret
    '''
    config = read_config()
    auth = tweepy.OAuthHandler(consumer_key=config['consumer_key'],
                               consumer_secret=config['consumer_secret'])
    print('navigate to: ' + auth.get_authorization_url())
    print('return with the pin')
    pin = input('type the pin here:')
    auth.get_access_token(pin)
    config['access_token'] = auth.access_token
    config['access_token_secret'] = auth.access_token_secret
    write_config(config)
    return config


def main():
    '''
    connects the pieces to grab posts from reddit and throw them on twitter
    '''
    reddit_connection = setup_reddit_connection()
    posts = []
    for source_subreddit in source_subreddits:
        posts.extend(get_posts(reddit_connection, source_subreddit))
        time.sleep(30)
    # should interleave all the posts since id should be cross site.
    posts.sort(key=lambda x: x.id)
    tweeter(posts)


def bootstrap_source(reddit_connection, source_subreddit):
    for post in get_posts(reddit_connection, source_subreddit):
        add_id_to_file(post.id)
        time.sleep(30)


if __name__ == '__main__':
    main()
