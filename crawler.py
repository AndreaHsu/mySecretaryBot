import nltk
from newspaper import Article
import newspaper

import jieba
from jieba.analyse import extract_tags
jieba.case_sensitive = True 
import re


def urlfind(string): 
    # findall() 查找匹配正则表达式的字符串
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url 

def crawl(url):
    
    news = Article(url)#, language='zh')
    news.download()        # 加载网页
    news.parse()           # 解析网页
    keywords = jieba.analyse.extract_tags(news.text, topK=20, withWeight=False)
    
    """
    print('题目：',news.title)       # 新闻题目
    print('正文：\n',news.text)      # 正文内容    
    print("============================================================")
    print(news.authors)     # 新闻作者
    print("============================================================")
    print(news.keywords)    # 新闻关键词
    print("============================================================")
    print(news.top_image) # 配图地址
    print("============================================================")
    
    source = newspaper.build(url)
    for category in source.category_urls():
        print(category)
    """
    if(news.text == None):
        text = news.title
    else:
        text = news.text
    # print(news.html)      # 网页源代码
    # print(news.summary)     # 新闻摘要
    # print(news.movies)    # 视频地址
    # print(news.publish_date) # 发布日期
    print(jieba.analyse.extract_tags(text, topK=20, withWeight=False))
    
    return news.title,text,keywords,news.top_image
def crawl_only_text(url):
    news = Article(url)#, language='zh')
    news.download()        # 加载网页
    news.parse()           # 解析网页
    
    if(news.text == None):
        text = news.title
    else:
        text = news.text
    print(text)
    return text