#!/usr/bin/env python2
# coding:utf-8

from twython import Twython
from colors import const
#import const
import numpy as np
import PIL.Image as img
import colorsys
import StringIO
import os
from datetime import datetime
from datetime import timedelta
from random import randint

number_of_colours = 1094

def is_morning():
    return 6 <= (datetime.utcnow() + timedelta(hours=9)).hour <= 9

class Colour(object):
    def __init__(self, name, hexcode, url):
        self.name = name
        # 0-255
        self.hexcode = hexcode
        self.rgb = tuple(
            int(hexcode[i:i+2],16) for i in range(0,6,2)
        )
        self.hsv = tuple(
            colorsys.rgb_to_hsv(*map(lambda x: x/255.0, self.rgb)))
        self.url = url or "https://en.wikipedia.org/wiki/{}".format(
            name.replace(' ','_'))
    
    @staticmethod
    def from_string(line):
        name,code,url = line.strip('\n').split('\t')
        return Colour(name, code, url)
    
    def to_string(self):
        hsv_to_show = [
            int(self.hsv[0]*360+0.5),
            int(self.hsv[1]*100+0.5),
            int(self.hsv[2]*100+0.5)
        ]
        hsv_str = "({}°, {}%, {}%)".format(*hsv_to_show)
        text = "{name} [hex:{code}, RGB:{rgb}, HSV:{hsv}] ({link})".format(
            name=self.name,
            code=self.hexcode,
            rgb=self.rgb,
            hsv=hsv_str,
            link=self.url)
        return text

    def to_image(self, size):
        colordata = np.array(list(self.rgb)*(size*size),
                             dtype=np.uint8).reshape(size,size,3)
        colorpic = img.fromarray(colordata)
        picdata = StringIO.StringIO()
        colorpic.save(picdata,format='png')
        picdata.seek(0)
        return picdata

    def is_light(self):
        return self.hsv[2] > 0.5

class ColoursBot(object):
    
    def __init__(self, keys=const.keys, size=200,
                 ncolour = number_of_colours,
                 fileloc=os.path.dirname(__file__)+'/colors_simp_with_link.txt'):
        try:
            self.api = Twython(keys['api_key'],keys['api_secret'],
                          keys['access_token'], keys['access_token_secret'])
        except Exception as e:
            print("An error occured in initialization.\n{}".format(e))
        
        self.ncolour=ncolour
        self.fileloc=fileloc
        self.size=size
        with open(fileloc, 'r') as f:
            self.colors = list(map(Colour.from_string,f))

    def pick_colour(self):
        if is_morning():
            colors = list(filter(lambda c: c.is_light(), self.colors))
        else:
            colors = self.colors
        n_max = len(colors)
        return colors[randint(0,n_max-1)]
    
    def update(self):
        c = self.pick_colour()
        text = c.to_string()
        picdata = c.to_image(self.size)
        # https://twython.readthedocs.org/en/latest/usage/advanced_usage.html
        self.api.update_status_with_media(
            status=text, media=picdata)
        return c

if __name__ == "__main__":
    a = ColoursBot()
    print(a.update())
