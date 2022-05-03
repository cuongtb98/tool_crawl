
from bs4 import BeautifulSoup
import multiprocessing
import requests
import html_text
import re

config = {
    "process": "",
    "threads": 10, #multiprocessing.cpu_count(),
    
    "fieldnames" : ['Title','Category', 'Content'],
    "url" : 'https://tiki.vn/search?q=qu%E1%BA%A7n+l%C3%B3t+nam',
    "file": "abc.csv",
    "contentItem": "newpaper3k" 
}


def get_list_items(source):
    soup = BeautifulSoup(source, 'html.parser')
    # ------------------------------------------------
    items = soup.find_all('a', class_='product-item')
    
    
    
    # ------------------------------------------------
    return items

def get_link_depen_items(itm , index, tool, Article):
    soup = BeautifulSoup(itm, 'html.parser')
    # ------------------------------------------------
    
    Link = "https://tiki.vn"+soup.find('a')['href']
    Title = soup.find('h3').text.strip()
    Category = soup.find('div', class_='price-discount__price').text.strip()
    
    
      
    # ------------------------------------------------ 
    Content = get_content_item(Link, tool, Article)
    data = {
        'Title': Title, 
        'Category': Category,
        'Content': Content
    }
    print(f"{index} crawl url: {Link}")
    return data


def get_content_item(url, tool, Article):
    if config['contentItem'] == 'newpaper3k':
        source = requests.get(url)
        soup = BeautifulSoup(source.text, 'html.parser')
        # ------------------------------------------------ 
        content = soup.find()
        
        # ------------------------------------------------ 
        content = html_text.extract_text(content, guess_layout=False)
        content = re.sub("[\s+|\n|\t]", " ", content)
        content = tool.correct(content)
        return content     
    elif config['contentItem'] == 'bs4':
        article = Article(url)
        article.download()
        article.parse()
        content = article.text
        content = re.sub("[\s+|\n|\t]", " ", content)
        content = tool.correct(content)
        return content
