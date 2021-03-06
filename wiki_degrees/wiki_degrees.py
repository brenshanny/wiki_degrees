#!/usr/bin/env python
"""
This script takes a wikipedia url and prints out another wikipedia
url X links away: aka the wikipedia degrees of freedom.

Inputs:
-url: a wikipedia url (required)
-o: a flag to toggle printing the urls and page titles of each link traversed
-d: the degrees of freedom away from the initial url. Default is 5

Author: Brendan Shanny
"""
import argparse
from bs4 import BeautifulSoup
from PIL import Image
import requests
import random
from StringIO import StringIO


# Links to avoid
null_links = [
    'Special:', 'File:', 'Portal:', 'Main_Page',  'Category_talk:',
    'Wikipedia:', ':', '#', 'index.php', 'wikimediafoundation.org',
    'mediawiki.org'
]


# Grab a random integer
def rand_int(max_int):
    return random.randint(0, max_int - 1)


# Create a BeautifulSoup object from a url
def soupify(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# Grab the links from a soup object
def grab_links(soup):
    return [link['href'] for link in soup.find_all('a', href=True)]


# Parse the title from the soup object
def grab_title(soup):
    try:
        title = str(soup.title.contents[0]).split('-')[0]
    except UnicodeEncodeError:
        print "ERROR"
        title = soup.title.contents[0]
    return title


# Format a link and check for unwanted links
def beautify_link(link):
    try:
        link = str(link)
    except UnicodeEncodeError:
        return None
    if any(null_link in link for null_link in null_links):
        return None
    if link[:4] == 'http':
        return link
    elif link[:5] == '/wiki':
        return "https://en.wikipedia.org{}".format(link)
    else:
        return None


# Filter out None links
def filter_links(links):
    return [link for link in links if link is not None]


# Try to find the most relvant image on a wiki page
# This needs some work
def find_image(soup):
    skip = ['featured', 'Sound-', 'logo', 'icon']
    imgs = [img['src'] for img in soup.find_all('img', src=True)]
    # Hopefully first one is the most appropriate img for the url
    im_url = None
    i = 0
    while im_url is None or any(s for s in skip if s in im_url):
        im_url = "https:{}".format(imgs[i])
        i += 1
    return Image.open(StringIO(requests.get(im_url).content))


# call find_image and save it
def grab_and_save_im(soup, filename):
    im = find_image(soup)
    im.save(filename)


# Main function to find a random page on wikipedia
def find_random_page(url, degrees, output=False):
    try:
        str(url)
    except UnicodeEncodeError:
        raise Exception("Cannot parse url! Unicode Error")
    previous = []
    while degrees > 0:
        previous.append(url)
        soup = soupify(url)
        if output:
            print("Url: {}      Title: {}".format(url, grab_title(soup)))
        links = grab_links(soup)
        beauty_links = [beautify_link(link) for link in links]
        all_links = filter_links(beauty_links)
        next_link = None
        while next_link is None and next_link not in previous:
            next_link = all_links[rand_int(len(all_links))]
        url = next_link
        degrees -= 1
    return url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', '--url', type=str, required=True)
    parser.add_argument('-o', '--output', action='store_true', required=False)
    parser.add_argument('-d', '--degrees', type=int, required=False)
    opts = parser.parse_args()
    if not opts.degrees:
        degrees = 5
    else:
        if opts.degrees > 0:
            degrees = opts.degrees
        else:
            degrees = 5
    end_url = find_random_page(opts.url, degrees, opts.output)
    print("With {} degrees of wikipedia, you went from\n{}\nto\n{}".format(
        degrees, grab_title(soupify(opts.url)), grab_title(soupify(end_url))))
