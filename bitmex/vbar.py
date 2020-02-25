import math
import json
import yaml
import websocket
from pprint import pprint
from termcolor import colored
from websocket import create_connection

BASEURL = 'wss://www.bitmex.com/realtime'

def sock_connect():
  ws = create_connection(BASEURL)
  #ws.send(json.dumps({"op": "subscribe", "args": ["trade:XBTUSD"]}))
  ws.send(json.dumps({"op": "subscribe", "args": ["tradeBin1m:XBTUSD"]}))
  while True:
    response = ws.recv()
    if 'action' in response and yaml.safe_load(response)['action'] == "partial":
#      print("Exiting the while loop, because \"action\":\"partial\"")
      break
  while True:
    on_balance_volume(ws.recv())   
    print('')

def on_balance_volume(response):
  current_volume = yaml.safe_load(response)['data'][0]['volume']
  current_open = yaml.safe_load(response)['data'][0]['open']
  current_close = yaml.safe_load(response)['data'][0]['close']

  if current_open < current_close:
    evol = current_volume / 100000
    for i in range(1,int(math.ceil(evol)),1):
      print(colored('\u0916', 'green', 'on_green'), end = "")

  elif current_open > current_close:
    evol = current_volume / 100000
    for i in range(1,int(math.ceil(evol)),1):
      print(colored('\u0916', 'red', 'on_red'), end = "")

  else:
    evol = current_volume / 100000
    for i in range(1,int(math.ceil(evol)),1):
      print(colored('\u0916', 'yellow', 'on_yellow'), end = "")

def main():
  sock_connect()

if __name__ == "__main__":
  main()
