#!/usr/bin/env python
# coding: utf-8

import urllib2
import datetime
import pickle
from progressbar import *

reload(sys)
sys.setdefaultencoding( "utf-8" )

URL = "http://qt.gtimg.cn/q="
TOTAL = 731

def do_get_request(url):
    if not url:
        return ""
    request = urllib2.urlopen(url)
    result = request.read()

    return result


def get_stock_info(stock_id):
    stock_info = do_get_request(URL + stock_id)
    return stock_info


def analyze_stock_info(stock_info):
    if not stock_info:
        return None

    segs = stock_info.split('~')
    stock_dict = {
        'id': segs[2],
        'name': segs[1].decode('gbk'),
        'price': segs[3],
        'pe_ratio': float(segs[39]),
        'volume': segs[36],
        'poe': segs[46],
        'total': float(segs[45]),
        'highest': segs[41],
        'lowest': segs[42],
        'time': segs[30],
        'change': segs[32],
        'exchange_ratio': segs[38]

    }
    return stock_dict

def total_filter(s_dict):
    if not s_dict:
        return False

    if s_dict.get('total') > 0.1 and s_dict.get('total') < 100:
        return True
    else:
        return False

if __name__ == "__main__":
    sids = []
    with open("stock_ids.txt") as f:
        sids = f.readlines()

    sids = [sid.strip() for sid in sids]
    #sids.append('sz002415')

    progress = ProgressBar()
    for i in progress(range(TOTAL)):
        time.sleep(0.005)

    index = 0
    s_dict_list = []

    pbar = ProgressBar().start()
    for sid in sids:
        index += 1
        pbar.update(int((index/(TOTAL-1))*100))
        time.sleep(0.01)
        try:
            s_info = get_stock_info(sid)
            s_dict = analyze_stock_info(s_info)
            s_dict_list.append(s_dict)
        except:
            continue
        #print s_dict.get('name'),
        #print s_dict

    pbar.finish()
    date_str = str(datetime.datetime.now().date())
    s_time = s_dict_list[0]['time']
    s_date = s_time[0:4] + "-" + s_time[4:6] + "-" + s_time[6:8]

    if s_date != date_str:
        exit(2)

    with open("data/"+date_str, 'w') as f:
        pickle.dump(s_dict_list, f, 0)

    s_dict_list = filter(total_filter, s_dict_list)

    new_dict_list = sorted(s_dict_list,
        key=lambda s_dict: s_dict.get('pe_ratio'), reverse=False)


    #for item in new_dict_list:
    #    print item.get('pe_ratio')

    for i in range(30):
        print new_dict_list[i].get('name'),
        print new_dict_list[i]

