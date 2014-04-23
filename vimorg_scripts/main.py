#!/usr/bin/env python2
# coding:utf-8

'''
Fetch updates of vim.org/scripts and tweets it.
'''

import tweepy
from vimorg_scripts import const

import urllib2
import xml.etree.ElementTree as el
import contextlib
from collections import namedtuple

Scriptdata = namedtuple('Script', 'title url')

class Bot(object):
    
    def __init__(self, keys=const.keys, t_co_length=const.t_co_length,
                 rss_url = const.rss_url, ):
        try:
            auth = tweepy.OAuthHandler(
                keys['CONSUMER_KEY'], keys['CONSUMER_SECRET'])
            auth.set_access_token(
                keys['ACCESS_TOKEN'], keys['ACCESS_TOKEN_SECRET'])
            self.api = tweepy.API(auth)
        except tweepy.error.TweepError as e:
            print("An error occured in initialization.\n{}".format(e))
        
        self.t_co_length = t_co_length
        self.rss_url = rss_url
        self.lasturl = None
        self.fetch_last_update()
        self.untweeted_updates = []
    
    def fetch_last_update(self):
        lasttweets = self.api.user_timeline()
        for tweet in lasttweets:
            try:
                self.lasturl = tweet.entities['urls'][0]['expanded_url']
                return self.lasturl
            except IndexError:
                continue
        return None
    
    def fetch_script_updates(self):
        if not self.lasturl:
            self.fetch_last_update()
        with contextlib.closing(urllib2.urlopen(self.rss_url)) as rss:
            rssdata = rss.read()
        datatree = el.fromstring(rssdata)
        for item in datatree.iter('item'):
            title, link = map(lambda x : item.find(x).text, ['title','link'])
            if link == self.lasturl:
                break  # fetched all updates.
            else:
                self.untweeted_updates.append(Scriptdata(title, link))
    
    def make_update(self):
        self.fetch_script_updates()
        while self.untweeted_updates:
            script = self.untweeted_updates.pop()
            length_title_can_use = 140 - self.t_co_length - 1
            if len(script.title) > length_title_can_use:
                title = script.title[:length_title_can_use-3] = '..'
            else:
                title = script.title
            # Amazingplugin 1.2 -- the awsomeness http://vim.org/scripts/foo
            update_text = "{title} {url}".format(title=title, url=script.url)
            # now tweet
            self.api.update_status(update_text)

if __name__ == "__main__":
    bot = Bot()
    bot.make_update()
