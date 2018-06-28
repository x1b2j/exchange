import io
import time
import json
import ssl
import requests
import websocket
import threading
import datetime
import pandas as pd
import numpy as np
from pprint import pprint
from collections import deque
from termcolor import colored
from collections import Counter
#import matplotlib.pyplot as plt
from websocket import create_connection, WebSocketConnectionClosedException

BASEURL = 'wss://api.bitfinex.com/ws/'
daily_low_last_time = {}
daily_high_last_time = {}
queue = {}
symbols = "tBTCUSD,tLTCBTC,tETHBTC,tOMGBTC,tBCHBTC,tIOTABTC,tEOSBTC,tETCBTC,tXMRBTC,tDASHBTC,tZECBTC,tXRPBTC,tNEOBTC,tSANBTC"
for symbol in symbols.split(','):
    daily_low_last_time[symbol] = 0
    daily_high_last_time[symbol] = 0
    queue[symbol] = deque(maxlen=1000)

#. This function is to check if the socket is live.
def sock_connect_test():
    ping = {
               "event":"ping"
           }
    ws = create_connection(BASEURL)
    #. The first message is version information.
    ws.recv()
    ws.send(json.dumps(ping))
    pong_response = ws.recv()
    if 'pong' in pong_response:
        print("socket connectivity is OK.")
        return True
    else:
        print("some connectivity problem occured, closing the socket...")
        ws.close()
        exit()

def sock_connect(channel, symbols):
    try:
        sock_connect_test()
        ws = create_connection(BASEURL)
        for symbol in symbols.split(','):
            payload = {
                    "event": "subscribe",
                    "channel": channel,
                    "symbol": symbol
                    }
            ws.send(json.dumps(payload))
        global queue
        INTERVAL = 60 * 60
        while True:
            datum = json.loads(ws.recv())

            #. fix these if statements (combine them).
            if 'hb' not in datum:
                if 'event' not in datum:
                    if channel == "ticker":
                        queue[symbol].append((datum[-4], time.time()))
                        queue_as_list = [x[0] for x in list(queue[symbol]) if time.time() - x[1] < INTERVAL]
                        print(queue_as_list)
                        total = np.sum(queue_as_list)
                        print("average is: {}".format(total))

                        #.socket is getting disconnected. Need to fix.
                        time.sleep(1)
                    else:
                        if 'tu' in datum:
                            #. datum[-1] == amount traded (bought/sold)
                            buy = []
                            sell = []
                            queue[symbol].append((datum[-1], time.time()))
                            queue_as_list = [x[0] for x in list(queue[symbol]) if time.time() - x[1] < INTERVAL]
                            #print(queue_as_list)
                            buy.extend([x for x in queue_as_list if x > 0])
                            sell.extend([x for x in queue_as_list if x < 0])
                            '''
                            print("buy is: {}".format(buy))
                            print("sell is: {}".format(sell))
                            print("buy sum is: {}".format(np.sum(buy)))
                            print("sell sum is: {}".format(np.sum(sell)))
                            '''
                            try:
                                ratio = float(np.sum(buy))/float(-np.sum(sell))
                                if ratio <= 1:
                                    color = 'red'
                                else:
                                    color = 'green'
                                text = [
                                        "put/call for {}".format(symbol),
                                        "at {:<10} is".format(datum[-2]),
                                        colored("{}".format(ratio), color)
                                        ]
                                print(" ".join(text))
                                #ratio.plot()
                                #plt.show()
                                #print("ratio for {}, at price: {:<10}, is: {}".format(symbol,datum[-2],ratio))
                            except ZeroDivisionError:
                                pass

    except WebSocketConnectionClosedException:
        print("connection closed unexpectedly for: {}".format(symbol.strip('t')))

def sock_ticker_trades(channel="ticker", symbols="tLTCBTC"):
        t = threading.Thread(target=sock_connect, args=(channel,symbols,))
        t.start()

def rotate_cursor():
    while True:
        for cursor in '|/*-*\\':
            print("{}{}".format(cursor,'\b'))

def sock_low(datum, symbol):
    global daily_low_last_time
    daily_low, last = datum[-1], datum[-4]
    if daily_low >= last:
        daily_low_time = time.time()
        #if daily_low != daily_low_last and daily_low_time-daily_low_last_time > 15*3600:
        if daily_low_time-daily_low_last_time[symbol] > 5*3600:
            print("{}: new daily low  for {} is: {:<15}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),symbol.strip('t'),last))
            daily_low_last = daily_low
            daily_low_last_time[symbol]= daily_low_time
    else:
        pass
        #print("{} daily_low__time = {:<20} || daily_low__last_time = {}".format(symbol.strip('t'),time.time(),daily_low_last_time[symbol]))
        #print("..still daily low for {} is: {:<15}".format(symbol.strip('t'),daily_low))

def sock_high(datum, symbol):
    daily_high, last = datum[-2], datum[-4]
    global daily_high_last_time
    if daily_high <= last:
        daily_high_time = time.time()
        #if daily_high != daily_high_last and daily_high_time-daily_high_last_time > 15*3600:
        if daily_high_time-daily_high_last_time[symbol] > 5*3600:
            print("{}: new daily high for {} is: {:<15}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),symbol.strip('t'),last))
            daily_high_last = daily_high
            daily_high_last_time[symbol] = daily_high_time
    else:
        pass
        #print("{} daily_high_time = {:20} || daily_high_last_time = {}".format(symbol.strip('t'),time.time(),daily_high_last_time[symbol]))
        #print("..still daily high for {} is: {:<15}".format(symbol.strip('t'),daily_high))

def main():
    channels = "ticker,trades"
    symbols = 'tBTCUSD,tLTCBTC,tETHBTC,tOMGBTC,tBCHBTC,tIOTABTC,tEOSBTC,tETCBTC,tXMRBTC,tDASHBTC,tZECBTC,tXRPBTC,tNEOBTC,tSANBTC'
    #symbols = "tBTCUSD"
    for symbol in symbols.split(','):
        sock_ticker_trades('trades', 'tBTCUSD')
    #sock_ticker_trades('ticker', 'tLTCBTC')
    #print(sock_connect_test())
    #for channel in channels.split(','):
    #    sock_ticker_trades("ticker", symbols)

if __name__ == '__main__':
    main()
