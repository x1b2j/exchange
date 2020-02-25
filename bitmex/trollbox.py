import json
import yaml
import websocket
from websocket import create_connection
from termcolor import colored

#import yaml.reader
#import re

BASEURL = 'wss://www.bitmex.com/realtime'

def sock_connect():
  ws = create_connection(BASEURL)
  ws.send(json.dumps({"op": "subscribe", "args": ["chat"], "channelID": 1}))
  count = 0
  while (count < 5):
    ws.recv()
    count = count + 1

  while True:
    try:
      #yaml.reader.Reader.NON_PRINTABLE = re.compile(
      #u'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]')
      response=ws.recv()
      user = yaml.safe_load(response)['data'][0]['user']
      message = yaml.safe_load(response)['data'][0]['message']
      channel_id = yaml.safe_load(response)['data'][0]['channelID']
      if 'data' in response and channel_id == 1:
        if ('pump' or 'up' or 'moon' or 'bullish' or 'long now' or 'pamp') in message:
          print(colored(user, 'green', attrs=['underline']) + ' :: ' + colored((message), 'green'))
        elif ('dump' or 'down' or 'bearish' or 'short now' or 'panic') in message:
          print(colored(user, 'red', attrs=['underline']) + ' :: ' + colored((message), 'red'))
        else:
          if yaml.safe_load(response)['data'][0]['fromBot'] == "true" or '```' in response:
            print(colored(user, 'white') + ' :: ' + colored((message), 'white'))
          elif user == 'REKT':
            print(colored(user, 'white') + ' :: ' + colored((message), 'cyan'))
          else:
            print(colored(user, 'blue') + ' :: ' + colored((message), 'yellow'))
    except yaml.reader.ReaderError:
      continue

def main():
  sock_connect()

if __name__ == "__main__":
  main()
