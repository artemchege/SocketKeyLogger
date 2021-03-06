import socket
import datetime
import time
import os

"""
Делаем передачу файлов через сокеты по локалке.
Через global IP еще не научился, нужно настраивать машрутизатор (переадресацию пакетов на сервер сюда).
Ввиду того что сокеты работают по локалке IP адрес будет внутренний. Что бы посмотреть внутренний адрес
в cmd нужно ввести ipconfig, поле ipv-адрес. Это адрес внутри локалки.
Мы создали объект sock, который является экземпляром класса socket. 
Для этого мы вызвали метод из модуля socket с именем socket и передали ему два параметра — AF_INET и SOCK_DGRAMM. 
AF_INET означает, что используется IP-протокол четвертой версии. 
При желании можно использовать IPv6. 
Во втором параметре для наших целей мы можем указать одну из двух констант: SOCK_DGRAMM или SOCK_STREAM. 
Первая означает, что будет использоваться протокол UDP. Вторая — TCP.
Вся передача через сокеты проходит в байтах, поэтому перед передачей любую строку надо закодировать example.encode().
И после на стороне клиента можно декодировать example.decode() что бы получить снова строку. Decode() принимает также кодировку,
но по умолчанию все и так работает.
Деплой сервера происходил на linode, сервер убунту последней версии. Все команды через SSH, где сервер это ip-адрес сервера, 
логин root, пароль в заметке в телефоне. FTP сервер тоже самое, порт 22 или пустой. SSH через PuTTy. 
"""
#создаем сокет:
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #можем прописать сокет явно
#sock = socket.socket() #видимо по умолчанию тоже работает

#UDP обернул в функцию, работает по сути точно также как и TCP
def listen_udp():
    sock = socket.socket()
    # UDP слушатель
    sock.bind(('', 9090))
    result = sock.recv(1024)
    print(result)
    print('Message:', result.decode('utf-8'))
    sock.close()

def listen_tcp():
    sock = socket.socket()
    print("TCP is started")

    #данная конструкция была нужна для хероку, там был динамический порт который можно было получить из внешнего окржуения
    try:
        PORT = int(os.environ['PORT'])
        print("Порт определен: ", PORT)
    except Exception as e:
        print("Произошла ошибка на этапе определения порта: ", e)

    #привязываем сокет к адресу и порту
    sock.bind(('', 9090))
    #адрес можно оставить пустым или прописать внутренний ip адрес, но не 127.0.0.1
    #если пустой то привязывается к любому свободному ip

    #указываем сколько запросов может стоять в очереди
    sock.listen(5)

    #запускаем бесконечный цикл, можно поставить try/except на прерывание через клаву
    while True:
        # распаковываем кортеж, когда что-либо принимаем через сокет
        conn, addr = sock.accept()

        #будем писать время
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        print("Наш conn: ", conn)
        print("Наш addr: ", addr)

        #в переменной conn находится  куча служебной информации об отправителе и получателе
        #в переменной addr находится инфа об ip-адресе отправителя и его порт(?)
        #print('conn: ', conn, "addr: ", addr)

        #принимаем данные по 1 килобайту, зачем не знаю, работает даже если и меньше кб
        data = conn.recv(1024)

        #присланные данные можно посмотреть через принт, также их можно декодировать из байтов в строку (просто уберутся служебные символы)
        #также в decode можно указать кодировку, если получаются кракозябры
        #print(data.decode(), current_time)

        print("Наша data: ", data.decode())

        #запишем еще все в файл на стороне сервера
        #with open("server_log.txt", "a") as w:
            #w.write(data.decode())
            #w.write(" ")
            #w.write(current_time)
            #w.write("\n")

        #далее мы можем обработать data и послать обратно через метод conn, который является экземпляром класса сокета
        conn.send(data.upper())

    #всегда закрываем коннект в конце
    conn.close()


def reversed_shell():
    print("Reversed shell is started")

    #Создаем сокет:
    sock = socket.socket()
    #Привязываем сокет:
    sock.bind(('', 9090))
    sock.listen(5)
    conn, addr = sock.accept()

    print("Наш addr: ", addr)

    data = conn.recv(1024)
    print("Наша data: ", data.decode())
    #далее проваливаемся в бесконечный цикл посыла команд с выходом по слову quit
    while True:
        cmd = input("waiting for input: ")
        if cmd == "quit":
            conn.send(cmd.encode())
            conn.close()
            break
        conn.send(cmd.encode())
        data = conn.recv(1024)
        """
        Потратив 2 часа времени было установлено что консоль CMD пишет результат в очень редкой кодировке cp866, которая кидала ошибки
        при попытке декодировать через win-1251 или utf-8. Клиент шлет байты, а тут на стороне сервере надо делать декод именно через cp866.
        Для других языков возможно будет по другому. Можно прописать игнорирование ошибок errors="ignore".
        """
        print(data.decode("cp866"))
    conn.close()

if __name__ == '__main__':
    reversed_shell()