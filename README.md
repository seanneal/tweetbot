# tweetbot

##summary
This is a simple project that I plan on running on a regular basis.  The idea is to grab content from reddit and have it automatically get tweeted.   So that I can easily see the stuff I'm interested in in my twitter feed.   

##history
I began with a script I found here: https://pythontips.com/2013/09/14/making-a-reddit-twitter-bot/

I brought the script into python 3.5 and ran it through pylint and autopep.  I also updated the API calls and eliminated the call to an external URL shortener since the tweet apis appear to do that automatically now.   

We have now hit MVP.   

##future goals 
The plan from here is to add some fancier processing to the reddit content and see about adding more value.

Here are the things off the top of my mind that I want to add: 
* Write a bash script that will pull updates from github automatically and run the bot every hour or so.  
* reconfigure the tweets so that we have direct links to reddit instead/in addition to the big link.   
* exclude links to imgur and any other domain that is questionable 
* some good hashtags for each subreddit.    
* Add some NLP to create my own headlines instead of re-using reddit titles 
* Add some NLP to generate hashtags on the fly 

In general, just want to keep this bad boy running.   
