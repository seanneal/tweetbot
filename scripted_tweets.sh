#!/bin/bash
cd ~/tweetbot/
echo beginning tweet bot > scripted_tweets.log
date >> scripted_tweets.log
git pull >> scripted_tweets.log
python3 tweet_bot.py >>scripted_tweets.log
date >> scripted_tweets.log
