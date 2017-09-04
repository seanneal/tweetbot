'''
First Version: Tweets contents from subreddits
'''
import time
import configparser
from collections import namedtuple
import praw
import tweepy

Post = namedtuple('Post', ['id', 'title', 'url',
                           'reddit_url', 'domain', 'user', 'subreddit_name'])


def strip_title(title):
    '''
    shortens title to fit in the tweet
    '''
    if len(title) < 94:
        return title
    else:
        return title[:93] + "..."


def get_posts(reddit_connection, subreddit_name):
    '''
    grabs posts from reddit and formats them for processing
    '''
    posts = []
    print('[bot] Getting posts from Reddit')
    subreddit = reddit_connection.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=20):
        post = Post(id=submission.id,
                    title=submission.title,
                    url=submission.url,
                    reddit_url=submission.shortlink,
                    domain=submission.domain,
                    user=submission.author.name,
                    subreddit_name=submission.subreddit.display_name
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


def main():
    '''
    connects the pieces to grab posts from reddit and throw them on twitter
    '''
    reddit_connection = setup_reddit_connection()
    posts = get_posts(reddit_connection, 'ethereum')
    tweeter(posts)


def filter_posts(posts):
    '''
    filters the posts
    '''
    filtered_domains = {'imgur.com'}

    def should_be_filtered(post):
        '''
        checks all relevant conditions
        '''
        return post.domain not in filtered_domains

    return (x for x in posts if not should_be_filtered(x))


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
        if not duplicate_check(post.id):
            print('[bot] Posting this link on twitter')
            print(post.title + ' ' + post.url + ' #bot')
            try:
                api.update_status(
                    post.title + ' ' + post.url + ' #bot')
            except Exception as e:
                print(e)
            add_id_to_file(post.id)
            time.sleep(30)


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


if __name__ == '__main__':
    main()
