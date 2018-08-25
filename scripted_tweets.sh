#!/bin/bash
pushd /home/seanneal/tweetbot/
echo beginning tweet bot 
git pull 
pipenv run python tweet_bot.py
popd
