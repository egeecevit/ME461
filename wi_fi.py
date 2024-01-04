#import socket
from time import sleep
import wifi
import os
import ipaddress
import socketpool
from math import *


HOST = '192.168.1.11'
PORT = 8081


print()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)
s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)


s.connect((HOST, PORT))

while True:
    buffer_size = 100
    receive_buffer = bytearray(buffer_size)
    bytes_received = s.recv_into(receive_buffer)

    received_msg = receive_buffer[:bytes_received].decode("utf8")
    try:
        res = eval(received_msg)
        msg_res = str(res)
        s.sendall(msg_res.encode())
    except:
        pass



