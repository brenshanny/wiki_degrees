#!/usr/bin/env python
"""
This is a twitter bot that will post two articles from wikipedia,
along with their degrees of wikipedia.

Written by: Brendan Shanny
"""

import os
from PIL import Image
import random
import tweepy
import time
import wiki_degrees


# grab the twitter api keys from env vars
if "DW_consumer_key" in os.environ.keys():
    consumer_key = os.environ["DW_consumer_key"]
else:
    raise Exception("Consumer Key not set as env var!")
if "DW_consumer_secret" in os.environ.keys():
    consumer_secret = os.environ["DW_consumer_secret"]
else:
    raise Exception("Consumer Secret not set as env var!")
if "DW_access_key" in os.environ.keys():
    access_key = os.environ["DW_access_key"]
else:
    raise Exception("Access Key not set as env var!")
if "DW_access_secret" in os.environ.keys():
    access_secret = os.environ["DW_access_secret"]
else:
    raise Exception("Access secret not set as env var!")

# authorize the twitter api
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


# A starting URL (The featured articles page of wikipedia)
url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"


def stitch_image(im1, im2):
    """ This function is designed to take two images, and create one
    image containing both images side by side"""
    if im1.size[1] > im2.size[1]:
        y = im1.size[1]
    else:
        y = im2.size[1]
    final = Image.new('RGB', ((im1.size[0] + im2.size[0]),
                              y))
    final.paste(im1, (0, 0, im1.size[0], im1.size[1]))
    final.paste(im2, (im1.size[0], 0, (im1.size[0] + im2.size[0]),
                      im2.size[1]))
    return final


def degrees_of_wiki():
    """ This function utilizes the wiki_degrees script to grab a random
    wikipedia page, and find another wikipedia page some random number of links
    away from it"""
    # Grad a random link from the featured articles page
    random_link = wiki_degrees.find_random_page(url, 1)
    # Grab the image from that page
    first_soup = wiki_degrees.soupify(random_link)
    first_im = wiki_degrees.find_image(first_soup)
    # Find a random page with x degrees of wiki away
    x = random.randint(1, 25)
    # Find a rondom wiki page, and (hopefully) grab its main image
    end_url = wiki_degrees.find_random_page(random_link, x)
    end_soup = wiki_degrees.soupify(end_url)
    end_im = wiki_degrees.find_image(end_soup)
    # Stitch these images together
    final_im = stitch_image(first_im, end_im)
    # setup the filename
    fn = os.path.expanduser(
            "~/.wiki_degrees_images/{}.png".format(time.time()))
    # Save the image
    final_im.save(fn)
    return (wiki_degrees.grab_title(first_soup),
            wiki_degrees.grab_title(end_soup), fn, x)


def push_to_twitter():
    # Grab the wikipedia page titles, image, and number of degrees
    title1, title2, fn, x = degrees_of_wiki()
    # Create the caption
    label = "{} => {} after {} degrees of wiki".format(title1, title2, x)
    # post to twitter
    api.update_with_media(fn, label)
    print label


def be_a_bot(t=1800):
    while True:
        push_to_twitter()
        time.sleep(t)
