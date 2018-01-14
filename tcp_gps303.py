'''
    TCP Socker Server handling data normalization from Coban GPS Tracker 303 tracking devices
'''

import socket
import sys
import csv
import json
import requests
from thread import *

HOST = '46.101.247.231'
PORT = 5001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(10)

def log(msg):
    with open('/home/django/gps303/log.txt', 'a+') as output_file:
        output_file.write('{0}\n'.format(msg))

def clientthread(conn):
    
    while True:

        data = conn.recv(1024)

        if not data:
            break

        print str(data)
        log(data)

        if data.find("##") > -1:
            conn.send("LOAD")

        if len(data) == 15:
            conn.send("ON")

	if len(data) > 26:
	    # imei:868683027373368,tracker,170328115724,,F,095721.000,A,5705.0812,N,02227.8471,E,0.00,0;
	    keys = ('imei', 'status', 'time', 'empty', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2', 'speed')

	    values = data.split(',')
	    stats = dict(zip(keys, values))

	    # convert dms to dd
	    lat = float(stats['c1'])
	    lon = float(stats['d1'])

	    lat_sign = -1 if lat < 0 else 1
	    lon_sign = -1 if lon < 0 else 1

	    lat_mm = lat % 100
	    lon_mm = lon % 100

	    lat_dd = (lat - lat_mm)/100
	    lon_dd = (lon - lon_mm)/100

	    lat_out = (lat_dd + lat_mm / 60) * lat_sign
	    lon_out = (lon_dd + lon_mm / 60) * lon_sign

	    stats['c1'] = round(lat_out, 6)
	    stats['d1'] = round(lon_out, 6)
	    stats['imei'] = stats['imei'][5:]
	    stats['speed'] = float(stats['speed'])

	    # data to send
	    stats_normalized = {
            'lat' : stats['c1'],
            'lon' : stats['d1'],
            'alt' : 0,
            'speed' : stats['speed'],
            'satelites' : 0,
            'bat_level' : 0,
            'car_voltage' : 0,
            'car_running' : 0,
            'imei' : stats['imei']
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
