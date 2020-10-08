"""

Клиент

"""
print("Проалились в подменю send на стороне клиента")

command, file_name = data.decode().split(" ")
print(file_name, " file_name")

f = open(file_name, 'wb')
# while True:
# print("Мы в начале true")
# data = sock.recv(1024)
# print(data, " data")
# print(len(data), " len data")
# if len(data) == 0:
# print("Мы в break")
# break
# file.write(data)
# print("Мы после write")

while (True):
    # receive data and write it to file
    l = sock.recv(1024)
    while (l):
        f.write(l)
        l = sock.recv(1024)

f.close()
print("В конце блока send, клиент, значит файл получен")

"""
сервер
"""

command, file_name = cmd.split(" ")
conn.send((f"send {file_name}").encode()) #подгатавливаем клиента к приему

f = open(file_name, "rb")
l = f.read(1024)
while (l):
    conn.send(l)
    l = f.read(1024)
f.close()
#data = op.read(1024000000) #читаем 10000 кб
#conn.send(data) #100 кб шлем разом одним пакетом

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