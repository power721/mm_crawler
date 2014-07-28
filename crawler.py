#!/usr/bin/env python
# -*- coding=utf8 -*-

import os
import urllib2
import socket
from bs4 import BeautifulSoup

class Crawler:
  '''
  a Crawler for images
  '''

  count = 0
  def __init__(self, baseUrl):
    self.req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    self.req_timeout = 20
    self.retry = 3
    self.page = 1
    self.image = 1
    self.maxCount = 0
    self.baseUrl = baseUrl
    self.pageUrl = ''
    self.imageUrl = ''
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
        raise RuntimeError, 'cannot open url: %s'%url
    except socket.timeout as e:
        if self.retry:
          self.retry -= 1
          return self.user_agent(url)
        else:
          print e
          raise RuntimeError, 'cannot open url'

    return html

  def parse(self, url):
    html = self.user_agent(url)
    self.soup = BeautifulSoup(html)
    #print 'parse url: ', url
    return self.soup


  def save_image(self, filename):
    if os.path.exists(filename):
      return False

    content = self.user_agent(self.img).read()
    with open(filename, 'wb') as image:
      image.write(content)
      Crawler.count += 1
    print 'save_image(%d): %s  filename: %s'%(Crawler.count, self.img, filename)

    return True
