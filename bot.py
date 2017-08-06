import os
from PIL import Image
import random
import tweepy
import time
import wiki_degrees


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


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"


def stitch_image(im1, im2):
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
    # Grad a random link from the featured articles page
    random_link = wiki_degrees.find_random_page(url, 1)
    # Grab the image from that page
    first_soup = wiki_degrees.soupify(random_link)
    first_im = wiki_degrees.find_image(first_soup)
    # Find a random page with x degrees of wiki away
    x = random.randint(1, 25)
    end_url = wiki_degrees.find_random_page(random_link, x)
    end_soup = wiki_degrees.soupify(end_url)
    end_im = wiki_degrees.find_image(end_soup)
    final_im = stitch_image(first_im, end_im)
    fn = os.path.expanduser(
            "~/.wiki_degrees_images/{}.png".format(time.time()))
    final_im.save(fn)
    return wiki_degrees.grab_title(first_soup), wiki_degrees.grab_title(end_soup), fn, x


def push_to_twitter():
    title1, title2, fn, x = degrees_of_wiki()
    label = "{} => {} after {} degrees of wiki".format(title1, title2, x)
    api.update_with_media(fn, label)
    print label


def be_a_bot():
    while True:
        push_to_twitter()
        time.sleep(600)
