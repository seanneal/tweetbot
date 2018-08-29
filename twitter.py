'''
First Version:  contents from subreddits
'''
import configparser
from collections import namedtuple
import tweepy

Tweet = namedtuple('Tweet', ['Primary', 'Second'])


class Twitter:
    '''
        class to load config info and send tweets
    '''

    def __init__(self):
        config = Twitter.__read_config()
        auth = tweepy.OAuthHandler(
            config['consumer_key'],
            config['consumer_secret'])
        auth.set_access_token(
            config['access_token'],
            config['access_token_secret'])
        self.__api = tweepy.API(auth)

    def send_tweet(self, message, reply_id=None):
        '''
        sends a tweet and prints any errors.
        '''
        try:
            if reply_id:
                status = self.__api.update_status(message, reply_id)
            else:
                status = self.__api.update_status(message)
        except tweepy.TweepError as tweep_error:
            print(tweep_error)
        return status

    @staticmethod
    def __read_config():
        '''
        reads from 'tweepy.ini' which must be in the working directory
        '''
        config = configparser.ConfigParser()
        config.read('tweepy.ini')
        return {key: config['bot1'][key] for key in config['bot1']}

    @staticmethod
    def __write_config(config_dict):
        '''
        write 'tweepy.ini' with updated values
        '''
        config = configparser.ConfigParser()
        config.read('tweepy.ini')
        for key in config_dict:
            config['bot1'][key] = config_dict[key]
        with open('tweepy.ini', 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def refresh_access_token():
        '''
        interactive function that gets the access token and access token secret
        '''
        config = Twitter.__read_config()
        auth = tweepy.OAuthHandler(consumer_key=config['consumer_key'],
                                   consumer_secret=config['consumer_secret'])
        print('navigate to: ' + auth.get_authorization_url())
        print('return with the pin')
        pin = input('type the pin here:')
        auth.get_access_token(pin)
        config['access_token'] = auth.access_token
        config['access_token_secret'] = auth.access_token_secret
        Twitter.__write_config(config)
        return config
