import math
import json
import yaml
import curses
import traceback
import websocket
from pprint import pprint
from websocket import create_connection
from termcolor import colored

BASEURL_SHITMEX = 'wss://www.bitmex.com/realtime'
BASEURL_COINBASE = 'wss://ws-feed.pro.coinbase.com'

def coinbase_sock_connect():
  ws = create_connection(BASEURL_COINBASE)
  ws.send(json.dumps({
    "type": "subscribe",
    "product_ids": [
        "BTC-USD"
    ],
    "channels": [
#      "full",
      "ticker",
#      "level2",
#      "heartbeat",
      {
        "name": "ticker",
        "product_ids": [
            "BTC-USD"
        ]
      }
    ]
  }))

  try:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    win1 = curses.newwin(30, 30, 0, 0)
    win1.border()
    while True:
      response = ws.recv()
      if 'subscriptions' in response:
        continue
      side = yaml.safe_load(response)['side']
      size = yaml.safe_load(response)['last_size']
      price = yaml.safe_load(response)['price']
      win1.addnstr(1, 2, price + ' ' + size, curses.A_BOLD)
      win1.refresh()
      ch = win1.getch()
      if ch == ord('q'):
        break
#      win1.clear()
      win1.clrtoeol()
#      win1.clrtobot()
      win1.refresh()
  except:
    traceback.print_exec()
  finally:
    win1.keypad(0)
    #stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

'''
    #print("{:20} {:20}".format(colored(price, colour), colored(size, colour)))
      if side == 'buy':
        colour = 'green'
      else:
        colour = 'red'
'''

def shitmex_sock_connect():
  ws = create_connection(BASEURL_SHITMEX)
  ws.send(json.dumps({"op": "subscribe", "args": ["trade:XBTUSD"]}))

  while True:
    response = ws.recv()
    if 'action' in response and yaml.safe_load(response)['action'] == "partial":
      print("Exiting the while loop, because \"action\":\"partial\"")
      break

  try:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    win1 = curses.newwin(30, 30, 0, 0)
    win1.border()
    while True:
      response=ws.recv()
      if 'data' in response:
#        timestamp = yaml.safe_load(response)['data'][0]['timestamp']
#        symbol = yaml.safe_load(response)['data'][0]['symbol']
#        side = yaml.safe_load(response)['data'][0]['side']
        price = yaml.safe_load(response)['data'][0]['price']
        size = yaml.safe_load(response)['data'][0]['size']
        win1.addnstr(1, 2, str(price) + ' ' + str(size), curses.A_BOLD)
        ch = win1.getch()
      #  win1.clear()
        win1.clrtoeol()
        ch = stdscr.getch()
        if ch == ord('q'):
            break
        win1.refresh()
      #  win1.clrtobot()
#        win1.refresh()
  except:
    traceback.print_exec()
  finally:
    win1.keypad(0)
    #stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
#      if int(math.ceil(size/1000)) < 2:
#        print(colored('\u0916', colour, on_colour), end = "")
#      else:
#        for i in range(1,int(math.ceil(size/1000)),1):
#          print(colored('\u0916', colour, on_colour), end = "")

      #print("{:20} {:20}".format(colored(price, colour), colored(size, colour)))
      #print("{:20} {:20} {:20} {:20} {:20}".format(colored(timestamp, colour), colored(symbol, colour), colored(side, colour), colored(price, colour), colored(size, colour)))

def main():
  shitmex_sock_connect()
#  coinbase_sock_connect()

if __name__ == "__main__":
  main()

'''
    if 'l2update' in response:
      side = yaml.safe_load(response)['changes'][0][0]
      price = yaml.safe_load(response)['changes'][0][1]
      size = yaml.safe_load(response)['changes'][0][2]
      if side == 'buy':
        colour = 'green'
      else:
        colour = 'red'
      print("{:20} {:20}".format(colored(price, colour), colored(size, colour)))

{
  "type": "ticker",
  "sequence": 10878578482,
  "product_id": "BTC-USD",
  "price": "9819.99",
  "open_24h": "9986.55000000",
  "volume_24h": "9451.26364659",
  "low_24h": "9665.39000000",
  "high_24h": "10077.11000000",
  "volume_30d": "258888.13877306",
  "best_bid": "9819.98",
  "best_ask": "9819.99",
  "side": "buy",
  "time": "2019-09-23T18:39:41.195000Z",
  "trade_id": 74476314,
  "last_size": "0.01996233"
}
'''
