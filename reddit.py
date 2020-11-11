'''
code to interface with Reddit
'''
import configparser
import random
import praw
import duplicates
from twitter import Tweet


class Reddit:
    '''
    Encapsulate reddit access
    '''

    def __init__(self, tweet_length=276):
        self.__reddit_connection = praw.Reddit(
            'bot1', user_agent='bot1 user agent')
        self.__tweet_length = tweet_length
        self.__duplicates = duplicates.Duplicates('posted_tweets.txt')

    def __get_tweets(self, subreddit_name):
        '''
        grabs tweets from reddit and formats them for processing
        '''
        tweets = []
        print('[bot] Getting tweets from Reddit\\r\\{}'.format(subreddit_name))
        subreddit = self.__reddit_connection.subreddit(subreddit_name)
        filtered_domains = {'imgur.com'}

        should_be_filtered = \
            lambda domain, post_id, stickied: domain in filtered_domains or \
            self.__duplicates.duplicate_check(post_id) or \
            stickied

        for submission in subreddit.hot(limit=10):
            if not should_be_filtered(
                    submission.domain,
                    submission.id,
                    submission.stickied):
                first, second = self.__convert_post_to_tweet(
                    submission.title,
                    submission.author.name,
                    submission.is_self,
                    submission.subreddit.display_name,
                    submission.url,
                    submission.shortlink)
                tweets.append(Tweet(first, second))
                self.__duplicates.add_id(submission.id)
        return tweets

    @staticmethod
    def __shorten_title(title, max_len):
        '''
        shortens title to fit in the tweet
        '''
        if len(title) <= max_len:
            return title
        return title[:max_len - 3] + "..."

    def __convert_post_to_tweet(
            self,
            title,
            user,
            is_self,
            subreddit_name,
            url,
            reddit_url):
        '''
        split the post into two tweets, one primary and one that is the reply.
        keep all the communication here.
        '''
        user_preamble = 'u/{user} says: '.format(user=user)
        hash_tag = '#{tag}'.format(tag=subreddit_name)
        shortened_title = self.__shorten_title(
            title,
            self.__tweet_length -
            23 -
            len(user_preamble) -
            len(hash_tag))
        primary_tweet = user_preamble + shortened_title + ' ' + url + ' ' + hash_tag
        reply_tweet = ''
        if not is_self:
            reply_tweet = 'further discussion to be had here: {url}'.format(
                url=reddit_url)
        return primary_tweet, reply_tweet

    def __bootstrap_source(self, source_subreddit):
        subreddit = self.__reddit_connection.subreddit(source_subreddit)
        for post in subreddit.hot(limit=10):
            self.__duplicates.add_id(post.id)

    def __get_subreddits(self):
        def empty(subreddit_name):
            return not subreddit_name or subreddit_name.isspace()

        def parse_list(line):
            return [x for x in line.splitlines() if not empty(x)]

        CONFIG_FILE = 'subreddits.ini'
        CONFIG_SECTION = 'subreddits'
        CONFIG_NEW = 'new'
        CONFIG_KNOWN = 'known'

        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_FILE)
        subreddits_cfg = cfg.get(CONFIG_SECTION, CONFIG_KNOWN)
        subreddits = parse_list(subreddits_cfg)

        new_subreddits = cfg.get(CONFIG_SECTION, CONFIG_NEW)
        if not empty(new_subreddits):
            subreddits_cfg = subreddits_cfg + new_subreddits
            cfg[CONFIG_SECTION][CONFIG_NEW] = ''
            cfg[CONFIG_SECTION][CONFIG_KNOWN] = subreddits_cfg
            with open(CONFIG_FILE, 'w') as cfg_file:
                cfg.write(cfg_file)
            new_subreddits = parse_list(new_subreddits)
            for subreddit in new_subreddits:
                self.__bootstrap_source(subreddit)
                subreddits.append(subreddit)

        if not subreddits:
            print('error: subreddit list is totally empty')

        return subreddits

    def get_tweets(self):
        '''
        Get's posts from reddits and converts them to tweets.
        '''
        tweets = []
        for subreddit in self.__get_subreddits():
            for tweet in self.__get_tweets(subreddit):
                tweets.append(tweet)
        random.shuffle(tweets)
        return tweets
