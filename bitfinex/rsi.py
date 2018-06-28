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
queue = {}
last_time = {}
symbols = "tBTCUSD,tLTCBTC,tETHBTC,tOMGBTC,tBCHBTC,tIOTABTC,tEOSBTC,tETCBTC,tXMRBTC,tDASHBTC,tZECBTC,tXRPBTC,tNEOBTC,tSANBTC"
for symbol in symbols.split(','):
    last_time[symbol] = 0
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
    global last_time
    global last_price
    last_time[symbol] = int(time.time())
    INTERVAL = 5 * 60
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
                        #. datum[-2] == price
                        #. datum[-3] == timestamp
                        buy = []
                        sell = []
                        queue[symbol].append((int(datum[-3]), datum[-2]))
                        queue_as_list = [x[1] for x in list(queue[symbol]) if x[0] - last_time[symbol] < INTERVAL]
                        last_price = queue_as_list[0]
                        curr_price = queue_as_list[-1]
                        print("momentum = {}".format(momentum(last_price,curr_price)))

                        '''
                        #series = pd.Series(np.array(queue_as_list))
                        if len(queue_as_list) > 50:
                            print(rsi(series))
                        else:
                            print("waiting for the first {} seconds, {}".format(INTERVAL,int(time.time())))
                        if int(time.time()) - last_time[symbol] >= INTERVAL:
                            print(rsi(series))
                        else:
                            print("waiting for the first {} seconds, {}".format(INTERVAL,int(time.time())))
                        #print(df.ewm(com=0.5).mean())
                        if int(time.time()) - last_time[symbol] >= INTERVAL:
                            df=df.append([datum[-3],datum[-2]], ignore_index=False)
                            print(df)
                            #last_time[symbol] = int(time.time())
                        else:
                            print("waiting for the first two minutes, {}".format(int(time.time())))
                            queue[symbol].append((int(datum[-3]), datum[-2]))
                            queue_as_list = [x for x in list(queue[symbol]) if x[0] - last_time[symbol] < INTERVAL]
                            df = pd.DataFrame(queue_as_list, index=[x[0] for x in queue_as_list], columns=['Timestamp',symbol])
                        '''

def momentum(last_price,curr_price):
    momentum = (curr_price/last_price)-1
    return float(momentum)

def rsi(data, window=14):
    delta = data.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[window - 1]] = np.mean(u[:window])
    u = u.drop(u.index[:(window - 1)])
    d[d.index[window - 1]] = np.mean(d[:window])
    d = d.drop(d.index[:(window - 1)])
    rs = u.ewm(com=window - 1,
            ignore_na=False,
            min_periods=0,
            adjust=False).mean() / d.ewm(com=window - 1,
                    ignore_na=False,
                    min_periods=0,
                    adjust=False).mean()
    res = 100 - 100 / (1 + rs)
    res.fillna(res.mean(), inplace=True)
    return res


def sock_ticker_trades(channel="ticker", symbols="tETHBTC"):
    t = threading.Thread(target=sock_connect, args=(channel,symbols,))
    t.start()

def main():
    channels = "ticker,trades"
    symbols = 'tBTCUSD,tLTCBTC,tETHBTC,tOMGBTC,tBCHBTC,tIOTABTC,tEOSBTC,tETCBTC,tXMRBTC,tDASHBTC,tZECBTC,tXRPBTC,tNEOBTC,tSANBTC'
    #symbols = "tBTCUSD"
    sock_ticker_trades('trades','tBTCUSD')
    '''
    for symbol in symbols.split(','):
        sock_ticker_trades('trades', symbol)
    sock_ticker_trades('ticker', 'tLTCBTC')
    print(sock_connect_test())
    for channel in channels.split(','):
        sock_ticker_trades("ticker", symbols)
    '''

if __name__ == '__main__':
    main()
