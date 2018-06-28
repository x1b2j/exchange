import next
import time
import sys
from termcolor import colored
from pprint import pprint
from collections import deque

INTERVAL = 60 * 30

def main():
    q = deque(maxlen=100000)
    for order in next.orders(sys.argv[1]):
        q.append((order, time.time()))
        now = time.time()
        q_as_list = [x[0] for x in list(q) if now - x[1] < INTERVAL]
        buy_orders = [x['Total'] for x in q_as_list if x['OrderType'] == 'BUY']
        sell_orders = [x['Total'] for x in q_as_list if x['OrderType'] == 'SELL']
        print("BUY {:10.3f} {} {} SELL {:10.3f}".format(
            sum(buy_orders),
            colored("{:<13}".format(order['Quantity']), "white"),
            colored("{:.8f}".format(order['Price']), "red" if order['OrderType'] == "SELL" else "blue"),
            sum(sell_orders)))

if __name__ == '__main__':
    main()
