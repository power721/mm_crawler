1.分析图片网站结构
图片网站有几个分类，随便选取一个分析：
  a.第一个分页的网页是index.html，后面的是index_%d.html的形式。
  b.图片列表在<div class="c_inner">里面，但是这个不是唯一的;
    首先找到<div class="ShowPage">，它的下一个兄弟节点就是目标，然后找到里面所有li.a，可以获取所有图片的网页地址。
    不能直接找a，因为后面有分页的链接。
  c.进入一个图片网页分析，查看网页源代码后得知图片地址是存放在JavaScript代码中的，需要用正则表达式提取。
    可能会得到多个图片地址，需要取最后一个。并且真实地址还需要转换。
    在分页里面找到下一页的链接。最后一张图片的是下一组图片链接，可以用作结束条件。


2.爬虫类的设计
 a.首先设计了一个基类用于封装公共方法。
 b.MmCrawler类用于抓取所有分页里面的图片链接。
 c.MmImageCrawler类用于抓取一个图集里面的所有图片并保存。
 详情见5.类的实现。


3.多线程设计
  采用生产者-消费者模型。
  一个生产者（MmCrawler）负责抓取分页所有的图集地址并添加到工作队列中;
  多个消费者（MmImageCrawler）负责从工作队列取出图集地址，抓取并保存这个图集的所有图片。
  设计了一个线程池（ThreadPool），生产者创建线程池，线程池创建多个消费者。
  线程池保存工作队列和消费者线程。
  所有消费者线程是后台线程，当主线程退出时，所有消费者也结束生命。
  为了让主线程响应按键事件，消费者线程不能阻塞。


4.命令行参数
  使用argparse模块能够非常方便的添加命令行参数，并且自动生成帮助文本。


5.类的实现
  a.Crawler基类
    user_agent()方法用于封装urllib2的请求。
    parse()方法获取网页并包装为BeautifulSoup对象。
    save_image()方法保存图片文件，如果图片已经存在则返回。

  b.StopException
    表示任务结束：
    达到图片数量限制时抛出;
    工作队列为空时抛出;
    分页结束时抛出;

  c.URLError
    表示打开url出错，连续两次无法打开分页url时抛出StopException。

  d.MmCrawler(crawler.Crawler)
    __init__()初始化父类，创建图片目录。
    next_page()获取下一个分页地址。
    image_list()获取当前页的图集地址列表。
    run()创建线程池，获取所有分页和图集地址列表加入到工作队列中。

  e.MmImageCrawler(crawler.Crawler, threading.Thread)
    __init__()初始化所有父类并启动线程。
    next_image()获取图集的下一个图片网页地址。
    get_image()获取图片的真实地址。
    file_name()根据图片页面名称和图片后缀生成图片文件名。
    do_work()每次获取一个图片并保存。
    run()从工作队列中取出一个图集地址并处理。

  f：ThreadPool
    __init__()产生指定数量的消费者线程。
    add_job()添加一个图集地址到工作队列中。
    wait_all()等待所有消费者线程结束。
    finished()判断所有线程是否已经结束。




Issues:
1.urllib2不能打开中文名字的文件  -- Fixed with urllib2.quote()
2.计数不正确，即使加了锁。