import json
import yaml
import websocket
from websocket import create_connection
from termcolor import colored

BASEURL = 'wss://www.bitmex.com/realtime'

def sock_connect():
  ws = create_connection(BASEURL)
  ws.send(json.dumps({"op": "subscribe", "args": ["trade:ETHUSD"]}))
  count = 0
  while (count < 5):
    ws.recv()
    count += 1
  while True:
    response=ws.recv()
    if 'data' in response:
      timestamp = yaml.safe_load(response)['data'][0]['timestamp']
      symbol = yaml.safe_load(response)['data'][0]['symbol']
      side = yaml.safe_load(response)['data'][0]['side']
      price = yaml.safe_load(response)['data'][0]['price']
      size = yaml.safe_load(response)['data'][0]['size']
      if side == 'Buy':
        colour = 'green'
      else:
        colour = 'red'
      print("{:20} {:20}".format(colored(price, colour), colored(size, colour)))
      #print("{:20} {:20} {:20} {:20} {:20}".format(colored(timestamp, colour), colored(symbol, colour), colored(side, colour), colored(price, colour), colored(size, colour)))

def main():
  sock_connect()

if __name__ == "__main__":
  main()
