#!/usr/bin/env python
# -*- coding=utf8 -*-

import os
import re
import crawler
import threading
import Queue

class MmCrawler(crawler.Crawler):
  '''
  抓取分页里面的图片列表
  '''
  def __init__(self, imageDir='./pics/', baseUrl='http://www.22mm.cc/mm/qingliang/', startPage=1, threads=10):
    crawler.Crawler.__init__(self, baseUrl)
    self.imageDir = imageDir
    self.page = startPage or 1
    self.threads = threads or 10
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
    for li in self.soup.find('div', attrs={'class' : 'ShowPage'}).next_sibling.find_all('li'):
      res.append('http://www.22mm.cc' + li.a.attrs['href'])

    return res

  def run(self):
    pool = ThreadPool(self.baseUrl, self.imageDir, self.threads)

    while self.next_page():
      print 'pageUrl:', self.pageUrl
      self.parse(self.pageUrl)
      for imageUrl in self.image_list():
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

  def reset(self, imageUrl):
    self.firstUrl = imageUrl
    self.imageUrl = ''

  def next_image(self):
    if not self.imageUrl:
      self.imageUrl = self.firstUrl
      return self.imageUrl

    next_url = self.soup.find('div', attrs={'class' : 'ShowPage'}) # 分页
    try:
      next_url = list(next_url.children)[2].attrs['href'] # 第二个是下一页链接
    except Exception as e:
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

  def do_work(self):
    while self.next_image():
      self.parse(self.imageUrl)
      try:
        self.get_image()
        if not self.save_image(self.file_name()):
          break
      except Exception as e:
        print e

  def run(self):
    while True:
      try:
        imageUrl = self.workQueue.get()
        self.reset(imageUrl)
        self.do_work()
      except Queue.Empty:
        break
      except:
        print sys.exc_info()
        raise


class ThreadPool:
  def __init__(self, baseUrl, imageDir, num_of_threads):
    self.workQueue = Queue.Queue()
    self.threads = []
    for i in range(num_of_threads):
      thread = MmImageCrawler(baseUrl, imageDir, self.workQueue)
      self.threads.append(thread)

  def wait_all(self):
    while len(self.threads):
      thread = self.threads.pop()
      if thread.isAlive():
        thread.join()

  def add_job(self, imageUrl):
    self.workQueue.put(imageUrl)



if __name__ == '__main__':
  mm = MmCrawler('./pic/')
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
