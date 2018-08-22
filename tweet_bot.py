'''
First Version: Tweets contents from subreddits
'''
from reddit import Reddit 
from tweets import Twitter 

def main():
    '''
    connects the pieces to grab posts from reddit and throw them on twitter
    '''
    reddit = Reddit()
    twitter = Twitter()
    for tweet in reddit.get_tweets():
        twitter.send_tweet(tweet.Primary, tweet.Second)

if __name__ == '__main__':
    main()
