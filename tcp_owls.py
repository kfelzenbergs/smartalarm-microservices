'''
    TCP Socker Server handling data normalization from TrackerOwls tracking devices
'''

import socket
import sys
import csv
import json
import requests
from thread import *

HOST = '46.101.247.231'
PORT = 4242

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(10)
print 'Socket now listening'


def log(msg):
    with open('/home/django/tcpowls/log.txt', 'a+') as output_file:
        output_file.write('{0}\n'.format(msg))

def clientthread(conn):

    while True:

        data = conn.recv(1024)

        if not data:
            break

        print str(data)
        log(data)

	if len(data) > 26:
	    # imei:868683027373368,tracker,170328115724,,F,095721.000,A,5705.0812,N,02227.8471,E,0.00,0;
	    # 861358033497793,0.000000,0.000000,0.000000,0,0,0,0.000000

	    values = data.split(',')

	    # Convert dms to dd
	    lat = float(values[1])
	    lon = float(values[2])

	    # Data to send
	    stats_normalized = {
            'lat' : values[1],
            'lon' : values[2],
            'alt' : values[3],
            'speed' : values[5],
            'satelites' : values[4],
            'bat_level' : 0,
            'car_voltage' : values[7],
            'car_running' : values[6],
            'imei' : values[0]
	    }

	    print stats_normalized
	    print "sending.."
	    
        r = requests.post('http://127.0.0.1:7777/stats_gateway/', json=stats_normalized)
	    print r.status_code

    conn.close()

while 1:
    conn, addr = s.accept()
    print 'Connection established with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(clientthread ,(conn,))

s.close()
