import threading
import time

j = 0
def start_logger():
    while True:
        print("Logger")
        #j+=1
        time.sleep(1)



def foo():
    i=0
    while True:
        print(i)
        i+=1
        time.sleep(2)


threadOne = threading.Thread(target=start_logger, name="start key logging")
threadTwo = threading.Thread(target=foo, name="start_foo")

threadOne.start()
threadTwo.start()
threadOne.join()
threadTwo.join()