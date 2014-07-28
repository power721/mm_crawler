#!/usr/bin/env python
# -*- coding=utf8 -*-

import urllib2
import socket
from bs4 import BeautifulSoup

class Crawler:
  '''
  a Crawler for images
  '''

  def __init__(self, baseUrl):
    self.req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    self.req_timeout = 20
    self.retry = 3
    self.page = 1
    self.image = 1
    self.count = 0
    self.maxCount = 0
    self.baseUrl = baseUrl
    self.pageUrl = None
    self.imageUrl = None
    self.imageDir = './'
    self.soup = None
    pass

  def user_agent(self, url):
    html = None
    try:
        url= urllib2.quote(url, safe='/:')
        req = urllib2.Request(url, None, self.req_header)
        html = urllib2.urlopen(req, None, self.req_timeout)
    except urllib2.URLError as e:
        print 'urllib2.URLError: ', e
        raise RuntimeError, 'cannot open url'
    except socket.timeout as e:
        if self.retry:
          self.retry -= 1
          self.user_agent(url)
        else:
          print e
          return None

    return html

  def parse(self, url):
    html = self.user_agent(url)
    self.soup = BeautifulSoup(html)
    print 'parse url: ', url
    return self.soup


  def save_image(self, filename):
    print 'save_image: ', self.img
    content = self.user_agent(self.img).read()
    with open(filename, 'wb') as image:
      image.write(content)
      self.count += 1
