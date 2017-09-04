'''
First Version: Tweets contents from subreddits
'''
import sys
import time
import configparser
import praw
import tweepy


def strip_title(title):
    '''
    shortens title to fit in the tweet
    '''
    if len(title) < 94:
        return title
    else:
        return title[:93] + "..."


def tweet_creator(subreddit_info):
    '''
    grabs posts from reddit and formats them for processing
    '''
    post_dict = {}
    post_ids = []
    exclude_domain = 'self.' + subreddit_info.display_name
    print('[bot] Getting posts from Reddit')
    for submission in subreddit_info.hot(limit=20):
        if not submission.domain == exclude_domain:
            post_dict[strip_title(submission.title)] = submission.url
            post_ids.append(submission.id)
    return post_dict, post_ids


def setup_connection_reddit(subreddit):
    '''
    Gets a connection to the subreddit.
    uses the config in praw.ini  needs to be in working directory
    see: http://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
    '''
    print('[bot1] setting up connection with Reddit')
    reddit = praw.Reddit('bot1', user_agent='bot1 user agent')
    return reddit.subreddit(subreddit)


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
    subreddit = setup_connection_reddit('ethereum')
    post_dict, post_ids = tweet_creator(subreddit)
    tweeter(post_dict, post_ids)


def tweeter(post_dict, post_ids):
    '''
    puts the posts on twitter
    '''
    config = read_config()
    auth = tweepy.OAuthHandler(
        config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'],
                          config['access_token_secret'])
    api = tweepy.API(auth)
    for post, post_id in zip(post_dict, post_ids):
        if not duplicate_check(post_id):
            print('[bot] Posting this link on twitter')
            print(post + ' ' + post_dict[post] + ' #bot')
            try:
                api.update_status(
                    post + ' ' + post_dict[post] + ' #bot')
            except:
                e = sys.exc_info()[0]
                print("Error: " + e)
            add_id_to_file(post_id)
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
