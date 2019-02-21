#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Andy'
SITENAME = "Andy's blog"
SITEURL = 'http://localhost:8000'

TWITTER_USERNAME = 'ibingfei'

PATH = 'content'

TIMEZONE = 'Asia/Hong_Kong'
DEFAULT_DATE = (2012, 3, 2, 14, 1, 1)

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('Jinja2', 'http://jinja.pocoo.org/'),
#          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/ibingfei'),
          ('github', 'https://github.com/andysuen'),)

DEFAULT_PAGINATION = 10

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},
                       'extra/favicon.ico': {'path': 'favicon.ico'},
                       'extra/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},}

FAVICON = '/favicon.ico'

PAGE_DIRS = ['pages']
ARTICLE_DIRS = ['articles']

ARTICLE_URL = 'blog/{date:%Y}/{slug}'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}.html'

SIDEBAR_DIGEST = 'Web developer'

SHOW_ARCHIVES = True
SHOW_FEED = False  # Need to address large feeds

MENUITEMS = [("Home", "/"), ("Archive", "/archives.html")]

DISPLAY_PAGES_ON_MENU = True

DISPLAY_CATEGORIES_ON_MENU = False

THEME = 'pelican-themes/pelican-blue'
# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True