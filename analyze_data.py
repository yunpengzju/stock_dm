#!/usr/bin/env python
# coding: utf-8

import datetime
import sys
import os
import pickle

reload(sys)
sys.setdefaultencoding( "utf-8" )

DATA_ROOT = "data"
LAST_N = 6
TOP_N = 5
SAFE_PE = 80
SAFE_RATIO = 1.08
JUMP_RATIO = 1.06
LOWEST_PRICE = 12

def split_date(date):
    if date:
        try:
            (year, month, day) = date.split("-")
            return (year, month, day)
        except:
            return None
    return None

def yestoday(date_str):
    if not date_str:
        return None

    (year, month, day) = split_date(date_str)

    num_day = int(day)
    num_month = int(month)
    num_year = int(year)

    num_day = num_day - 1
    if num_day == 0:
        num_day = 31
        num_month = num_month - 1

    if num_month == 0:
        num_month = 12
        num_year = num_year - 1

    return str(num_year) + "-" \
        + str("%02d"%(num_month) ) + "-" \
        + str("%02d"%(num_day) )

def tomorrow(date_str):
    if not date_str:
        return None

    (year, month, day) = split_date(date_str)

    num_day = int(day)
    num_month = int(month)
    num_year = int(year)

    num_day = num_day + 1
    if num_day == 32:
        num_day = 1
        num_month = num_month + 1

    if num_month == 13:
        num_month = 1
        num_year = num_year + 1

    return str(num_year) + "-" \
        + str("%02d"%(num_month) ) + "-" \
        + str("%02d"%(num_day) )

def last_n_days(today, n):
    if not today:
        return None

    if n <= 0:
        return None

    day = today
    day_strs = []
    while n:
        if is_file_exist(day):
            day_strs.append(day)
            n -= 1
        day = yestoday(day)

    return day_strs

def last_deal_day(today):
    if not today:
        return None
    day = today
    while True:
        if is_file_exist(day):
            return day
        day = yestoday(day)

def next_deal_day(today):
    if not today:
        return None
    day = today
    n = 100
    while True:
        n -= 1
        if n == 0:
            return None
        day = tomorrow(day)
        if is_file_exist(day):
            return day

def last_n_day(today, n):
    day = today
    while n:
        day = last_deal_day(day)
        if not day:
            return None
        day = yestoday(day)
        n -= 1
    return day

def next_n_day(today, n):
    day = today
    while n:
        day = next_deal_day(day)
        if not day:
            return None
        n -= 1
    return day

def is_file_exist(day_str):
    if not day_str:
        return False

    return os.path.exists(os.path.join(DATA_ROOT, day_str))

def get_value(day_str):
    if not day_str:
        return None

    day_data = []
    with open(os.path.join(DATA_ROOT, day_str), 'r') as f:
        day_data = pickle.load(f)

    new_list = {}
    for stock in day_data:
        new_list[stock.get('id')] = stock
    return new_list

def cal_mark(sid, n_day_values, n):
    total_volume = float(0.0)
    day = 1
    for day_value in n_day_values:
        try:
            total_volume += float(day_value.get(sid).get('volume'))
        except:
            print "ERROR" + sid
            return 0
        day += 1
    mark = float(total_volume)/float(n)
    return mark

def get_stock_mark(stock_marks, sid):
    mark = float(stock_marks.get(sid).get('value'))
    if mark <= 0.0001:
        return 1000000000
    return mark

def filter_stock(stock_list, last_n_day_values):
    res = []
    for stock in stock_list:
        try:
            cur_price = float(stock.get('price'))
            start_price = float(last_n_day_values[LAST_N-2].get(stock.get('id')).get('price'))
            last_highest = float(last_n_day_values[0].get(stock.get('id')).get('highest'))
            last_lowest = float(last_n_day_values[0].get(stock.get('id')).get('lowest'))
            last_2_price = float(last_n_day_values[1].get(stock.get('id')).get('price'))
            if cur_price > last_highest and cur_price > LOWEST_PRICE:
                if stock.get('pe_ratio') < SAFE_PE:
                    if cur_price < SAFE_RATIO * start_price:
                        res.append(stock)
        except:
            print "ERROR2:" + stock.get('id')
            continue
    return res

def sort_top_stock(date):
    days = last_n_days(date, LAST_N)
    print days
    last_day = days.pop(0)
    last_day_value = get_value(last_day)

    last_n_day_values = []
    for day in days:
        last_n_day_values.append(get_value(day))

    stock_marks = {}
    for sid, s_value in last_day_value.iteritems():
        mark = cal_mark(sid, last_n_day_values, LAST_N-1)
        stock_marks[sid] = {"value": mark, "s_dict": s_value}

    stock_list = []
    for sid, s_dict in last_day_value.iteritems():
        stock_list.append(s_dict)

    filter_stock_list = filter_stock(stock_list, last_n_day_values)
    sorted_stock_list = sorted(filter_stock_list, key=lambda s_dict: float(s_dict.get('volume'))/get_stock_mark(stock_marks, s_dict.get('id')), reverse=True)

    top_stocks = []
    for i in range(TOP_N):
        if i > len(sorted_stock_list) - 1:
            break
        stock = sorted_stock_list[i]
        # print stock.get('name'),
        # print stock.get('id'),
        # print "price: "+stock.get('price'),
        # print "pe_ratio: "+str(stock.get('pe_ratio')),
        # print "exchange: "+stock.get('exchange_ratio'),
        stock['sort'] = i
        stock['mark'] = float(stock.get('volume'))/get_stock_mark(stock_marks, stock.get('id'))
        top_stocks.append(stock)
    return top_stocks

def get_day_data(date):
    data = {}
    with open(os.path.join(DATA_ROOT, date), 'r') as f:
        data = pickle.load(f)
    return data


if __name__ == "__main__":
    date = ""
    period = 0

    try:
        date = sys.argv[1]
    except:
        date = str(datetime.datetime.now().date())

    try:
        period = int(sys.argv[2])
    except:
        period = 0

    is_today = False

    if date == "yestoday":
        date = last_deal_day(yestoday(str(datetime.datetime.now().date())))
        period = 1

    if period is not 0:
        date = last_n_day(last_deal_day(date), period)

    if date == str(datetime.datetime.now().date()):
        is_today = True

    next_day_data = []
    if not is_today:
        print "After date: " + next_n_day(date, period)
        next_day_data = get_day_data(next_n_day(date, period))

    last_day = last_deal_day(date)  # if date is a deal day, then return date
    print "Before date: " + last_day
    tops = sort_top_stock(last_day)
    yestoday_tops = sort_top_stock(last_deal_day(yestoday(last_day)))
    tomm_sum = float(0)
    for stock in tops:
        # warning = False

        # for s in yestoday_tops:
        #     if s.get('id') == stock.get('id'):
        #         if s.get('sort'):
        #             warning = True
        # if warning:
        #     continue
        sid = stock.get('id')
        print stock.get('name'),
        print stock.get('id'),
        print "price: "+stock.get('price'),
        print "change:" + stock.get('change'),
        print "pe_ratio: "+str(stock.get('pe_ratio')),
        if is_today:
            print "exchange: "+stock.get('exchange_ratio'),
            print 'mark: ' + str(stock.get('mark')),
            print date + ": " + str(stock.get('sort')),
            for s in yestoday_tops:
                if s.get('id') == stock.get('id'):
                    print "yestoday: " + str(s.get('sort')),
                    break
            else:
                print "yestoday: None",

        if not is_today:
            for stock_next in next_day_data:
                if stock_next.get('id') == sid:
                    tomm_sum += float(stock_next.get('change'))
                    print "After %d days: %s " % (period, stock_next.get('change'))
                    break
            else:
                print "tomm: None"
        else:
            print ""
    if not is_today:
        print "Increase_sum: " + str(tomm_sum)


    print "success"