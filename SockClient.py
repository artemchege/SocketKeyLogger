import socket
import time
import datatime
"""
Также как и на серверной стороне, здесь будут фигурировать внутренние локальные IP, которые 
можно посмотреть в ipconfig в cmd.
Далее и на клиентской стороне сперва надо создать сокет. 
"""

def despatch(ip, port, message):
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

despatch("192.168.200.156", 9090, "hi")
