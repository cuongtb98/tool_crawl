import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import items
import threading


def item_flag_last(threads_number, item_flag, list_items_total):
    if item_flag + threads_number < list_items_total:
        return item_flag + threads_number 
    return list_items_total

def get_data_thread(itm_links):
    """
    itm_links: list link (["url1", "url2", ...])
    len(itm_links) <= self.threads_number 
    """
    threads = []
    
    for i in range(items.config['threads']):
        threads += [threading.Thread(target=items.get_content_item(), args=(str(itm_links[i]), ))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
        
