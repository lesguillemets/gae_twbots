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
from random import randint

number_of_colours = 1094

class ColoursBot(object):
    
    def __init__(self, keys=const.keys, size=200,
                 ncolour = number_of_colours,
                 fileloc=os.path.dirname(__file__)+'/colors_simp_with_link.txt'):
        try:
            self.api = Twython(keys['api_key'],keys['api_secret'],
                          keys['access_token'], keys['access_token_secret'])
        except:
            print("An error occured in initialization.\n{}".format(e))
        
        self.ncolour=ncolour
        self.fileloc=fileloc
        self.size=size
    
    def update(self):
        n = randint(0,self.ncolour-1)
        with open(self.fileloc, 'r') as f:
            i = 0
            for line in f:
                if i==n:
                    colour = line
                    break
                else:
                    i+=1
        name,code,url = line.strip('\n').split('\t')
        if not url:
            url = "https://en.wikipedia.org/wiki/{}".format(
                name.replace(' ','_'))
        r,g,b = [int(code[i:i+2],16) for i in range(0,6,2)]
        hsv = list(colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0))
        hsv[0] = int(hsv[0]*360+0.5)
        hsv[1] = int(hsv[1]*100+0.5)
        hsv[2] = int(hsv[2]*100+0.5)
        hsv_str = "({}°, {}%, {}%)".format(*hsv)
        
        size = self.size
        colordata = np.array([r,g,b]*(size*size), dtype=np.uint8).reshape(
            size,size,3)
        colorpic = img.fromarray(colordata)
        picdata = StringIO.StringIO()
        colorpic.save(picdata,format='png')
        picdata.seek(0)
        # https://twython.readthedocs.org/en/latest/usage/advanced_usage.html
        text = "{name} [hex:{code}, RGB:{rgb}, HSV:{hsv}] ({link})".format(
            name=name, code=code, rgb=(r,g,b), hsv=hsv_str,link=url)
        self.api.update_status_with_media(
            status=text, media=picdata)
        return (name,code,r,g,b,url)

if __name__ == "__main__":
    a = ColoursBot()
    print(a.update())
