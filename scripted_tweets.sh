#!/bin/bash
pushd /home/emshon/tweetbot/
echo beginning tweet bot 
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
git pull 
pipenv run python tweet_bot.py
popd
