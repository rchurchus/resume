#!/usr/bin/env python
import sys
import argparse
import requests
import json
import time
import logging

'''
Playing around with a stock API I found, nothing special here, just another code sample
'''

def get_average_price():
    with open('stock_price.txt', 'r') as r:
        prices = []
        for line in r.readlines():
            prices.append(float(line.strip()))
    return sum(prices) / len(prices)

def get_stock_price(symbol):

    #p = {'https': 'https://internal.proxy:443'}
    url = 'https://api.iextrading.com/1.0/stock/{0}/batch?types=quote,news,chart%range=1m&last=10'.format(symbol)
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        d = response.json()
        jdata = json.dumps(d, indent=2)
        return d['quote']['iexAskPrice']
    elif response.status_code == 404:
        raise ValueError('Bad symbol: {0}'.format(symbol))
    else:
        raise Error('Unable to communicate with API')

def get_price(symbol, limit=3, sleep=1, debug=False):
    if(debug):
        logging.debug("Get price {0} times delayed by {1} seconds".format(limit, sleep))
    count = 0
    while (count <= limit):
        try:
            stock_price = get_stock_price(symbol)
            with open('stock_price.txt', 'a') as f:
                f.write(str(stock_price) + '\n')

        except ValueError, e:
            print 'Oops looks like we have a bad symbol: {0}'.format(symbol)
            sys.exit(1)
        except:
            print 'Oops something went wrong... can\'t connect?'
            sys.exit(2)
        count += 1
        time.sleep(sleep)    

def parse_args():
    parser = argparse.ArgumentParser(description="This is a stock quote script.")
    parser.add_argument('--symbol', '-s', action='store', required=True, dest='symbol', help='Stock quote symbol')
    parser.add_argument('--debug', '-d', action='store_true', dest='debug', help='Log DEBUG messages')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    get_price(args.symbol, 1, 1, True)
    print "Average price :: {0}".format(get_average_price())
    
