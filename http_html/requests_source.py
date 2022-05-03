import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import items

import multiprocessing
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from requests_html import HTMLSession
import csv
from .ultil import item_flag_last
import threading
import language_tool_python
from newspaper import Article




class TextResponse(object):
    __chromedriver_path = 'setting/driver/chromedriver'
    __threads_number = items.config['threads']
    def __init__(self):
        self.session = HTMLSession()
        self.chromedriver_path = TextResponse.__chromedriver_path
        self.url = items.config["url"]
        self.list_data = None
        self.fieldnames = items.config["fieldnames"]
        self.item_flag = 0
        self.tool = language_tool_python.LanguageTool('en-US')
        self.file = items.config['file']
        self.writer = None
    #---------- file ----------
    def open_file(self, file_name="data.csv", mode="a"):
        self.file = open(file_name, mode, newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()
        
    def close_file(self):
        self.file.close()

    def insert_file(self, data):
        try:
            self.writer.writerow(data)
        except Exception as e:
            print("=========> Error: ",e)
            pass
    #---------- end file ----------


    def get_source(self):
        """
        output:  list data(bs4)
        """
        try:
            source = self.session.get(self.url)
            list_data = items.get_list_items(source.text)
            if len(list_data) > 0:
                print("================> execute get_source: bs4")
                return source.text
            else:
                options = webdriver.ChromeOptions()
                options.headless = True
                driver = webdriver.Chrome(self.chromedriver_path, chrome_options=options)
                driver.get(self.url)
                source = driver.page_source
                list_data = items.get_list_items(source)
                driver.quit()
                if len(list_data) > 0:
                    print("================> execute get_source: webdriver")
                    return source
        except:
            print("================> execute get_source: None")
            pass

    def get_content_item(self, url):
        article = Article(url)
        article.download()
        article.parse()
        Content = article.text
        Content = Content.replace('\n',' ').replace('\t',' ')
        Content = re.sub("[\s+|\n|\t]", " ", Content)
        Content = self.tool.correct(Content)
        return Content
    
    def get_data_thread(self, source):
        """
        itm_links: list link (["url1", "url2", ...])
        len(itm_links) <= self.threads_number
        """
        threads = []
        for i in range(self.__threads_number):
            threads += [threading.Thread(target=items.get_link_depen_items, args=(source, ))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def get_data_save_file(self, itm , index, tool, Article):
        data = items.get_link_depen_items(itm , index, tool, Article)
       
        self.insert_file(data)

    def crawl(self):
        self.open_file(self.file)
        list_items = items.get_list_items(self.get_source())
        list_items_total = len(list_items)
        for itm in range(self.item_flag, list_items_total, self.__threads_number):
            itm_last = item_flag_last(self.__threads_number, self.item_flag, list_items_total)
            print(f'============> crawl link[{self.item_flag}:{itm_last}] / {list_items_total}')
            threads = []
            list_items_temp = list_items[self.item_flag: itm_last]
            for i in list_items_temp:
                # itm_links.append(items.get_link_depen_items(str(i)))
                index = f"({list_items_temp.index(i)+self.item_flag}/{list_items_total})"
                threads += [threading.Thread(target=self.get_data_save_file, args=(str(i), index, self.tool, Article))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            # print(itm_links)
            
            self.item_flag += self.__threads_number
           
