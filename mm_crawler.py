#!/usr/bin/env python
# -*- coding=utf8 -*-

import os
import re
import crawler
import threading
import time
import Queue

class MmCrawler(crawler.Crawler):
  '''
  抓取分页里面的图片列表
  '''
  def __init__(self, imageDir='./pics/', baseUrl='http://www.22mm.cc/mm/qingliang/', startPage=1, threads=10, maxCount=0):
    crawler.Crawler.__init__(self, baseUrl)
    self.imageDir = imageDir
    self.page = startPage or 1
    self.threads = threads or 10
    crawler.Crawler.maxCount = maxCount
    if not os.path.isdir(self.imageDir):
      os.mkdir(self.imageDir)

  def next_page(self):
    if not self.pageUrl:
      self.pageUrl = self.baseUrl
      return self.pageUrl # 第一页

    self.page += 1
    self.pageUrl = self.baseUrl + 'index_%d.html' % self.page
    return self.pageUrl

  def image_list(self):
    res = []
    try:
      for li in self.soup.find('div', attrs={'class' : 'ShowPage'}).next_sibling.find_all('li'):
        res.append('http://www.22mm.cc' + li.a.attrs['href'])
    except RuntimeError as e:
      print e

    return res

  def run(self):
    pool = ThreadPool(self.baseUrl, self.imageDir, self.threads)

    while self.next_page():
      print 'pageUrl:', self.pageUrl
      self.parse(self.pageUrl)
      for imageUrl in self.image_list():
        if pool.finished():
          raise crawler.StopException
        #time.sleep(0.1)
        pool.add_job(imageUrl)
    pool.wait_all()


class MmImageCrawler(crawler.Crawler, threading.Thread):
  '''
  抓取一个系列的图片
  '''
  def __init__(self, baseUrl, imageDir='./pics/', workQueue=None):
    threading.Thread.__init__(self)
    crawler.Crawler.__init__(self, baseUrl)
    self.imageDir = imageDir
    self.workQueue = workQueue
    self.re = re.compile('arrayImg\[0\]="(.*?)"')
    self.setDaemon(True)
    self.start()

  def next_image(self):
    if not self.imageUrl:
      self.imageUrl = self.firstUrl
      return self.imageUrl

    next_url = self.soup.find('div', attrs={'class' : 'ShowPage'}) # 分页
    try:
      next_url = list(next_url.children)[2].attrs['href'] # 第二个是下一页链接
    except RuntimeError as e:
      print 'next_image:', e
      next_url = ''

    self.imageUrl = ''
    if next_url and next_url[0] != '/': # '/'开始的url是下一组图片链接
      self.imageUrl = self.baseUrl + next_url
      return self.imageUrl

  def get_image(self):
    img = self.re.findall(str(self.soup))[-1] # 图片地址在JavaScript代码中
    self.img = img.replace('/big/', '/pic/')  # 真实地址需要转换
    return self.img

  def file_name(self):
    print 'imageUrl: ', self.imageUrl
    # 网页名字加图片后缀
    filename = self.imageDir + self.imageUrl[self.imageUrl.rindex('/')+1:-5] + self.img[self.img.rindex('.'):]
    filename = os.path.normpath(filename)
    return filename

  def do_work(self, imageUrl):
    self.firstUrl = imageUrl
    self.imageUrl = ''

    while self.next_image():
      self.parse(self.imageUrl)
      try:
        self.get_image()
        if not self.save_image(self.file_name()):
          break
      except RuntimeError as e:
        print e

  def run(self):
    while True:
      try:
        imageUrl = self.workQueue.get(timeout=3)
        self.do_work(imageUrl)
      except Queue.Empty:
        break
      except crawler.StopException:
        break


class ThreadPool:
  def __init__(self, baseUrl, imageDir, num_of_threads):
    self.workQueue = Queue.Queue()
    self.threads = []
    for i in range(num_of_threads):
      thread = MmImageCrawler(baseUrl, imageDir, self.workQueue)
      self.threads.append(thread)

  def wait_all(self):
    while threading.active_count() > 0:
      time.sleep(0.1)

  def add_job(self, imageUrl):
    self.workQueue.put(imageUrl)

  def finished(self):
    for thread in self.threads:
      if thread.is_alive():
        return False
    return True


if __name__ == '__main__':
  mm = MmCrawler()
  #mm = MmCrawler(maxCount=100)
  mm.run()

  #mm.parse('http://www.22mm.cc/mm/qingliang/')
  # #print mm.soup
  # mm.image_list()
  # mm.parse(mm.next_page())
  # mm.image_list()

  # baseUrl = 'http://www.22mm.cc/mm/qingliang/'
  # imageUrl = 'http://www.22mm.cc/mm/qingliang/PiaHPJmHeeePaiemP.html'
  # worker = MmImageCrawler(baseUrl)
  # worker.run()
