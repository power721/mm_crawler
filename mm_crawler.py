#!/usr/bin/env python
# -*- coding=utf8 -*-

import os
import re
import crawler

class MmCrawler(crawler.Crawler):
  '''
  抓取分页里面的图片列表
  '''
  def __init__(self, imageDir='./pics/'):
    baseUrl = 'http://www.22mm.cc/mm/qingliang/'
    crawler.Crawler.__init__(self, baseUrl)
    self.imageDir = imageDir
    if not os.path.isdir(self.imageDir):
      os.mkdir(self.imageDir)
      pass # 处理异常

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
    while self.next_page():
      self.parse(self.pageUrl)
      for imageUrl in self.image_list():
        worker = MmImageCrawler(self.baseUrl, imageUrl, self.imageDir)
        worker.run()


class MmImageCrawler(crawler.Crawler):
  '''
  抓取一个系列的图片
  '''
  def __init__(self, baseUrl, imageUrl, imageDir='./pics/'):
    crawler.Crawler.__init__(self, baseUrl)
    self.firstUrl = imageUrl
    self.imageDir = imageDir
    self.re = re.compile('arrayImg\[0\]="(.*?)"')

  def set_url(self, imageUrl):
    self.firstUrl = imageUrl

  def next_image(self):
    if not self.imageUrl:
      self.imageUrl = self.firstUrl
      return self.imageUrl

    next_url = self.soup.find('div', attrs={'class' : 'ShowPage'}) # 分页
    try:
      next_url = list(next_url.children)[2].attrs['href'] # 第二个是下一页链接
    except Exception as e:
      print 'next_image:', e
      next_url = None

    self.imageUrl = None
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
    print 'filename: ', filename
    return filename

  def run(self):
    while self.next_image():
      self.parse(self.imageUrl)
      try:
        self.get_image()
        self.save_image(self.file_name())
      except Exception as e:
        print e




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
  # worker = MmImageCrawler(baseUrl, imageUrl)
  # worker.run()
