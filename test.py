import sys

b = b"\x92\xae\xac \xa2 \xe3\xe1\xe2\xe0\xae\xa9\xe1\xe2\xa2\xa5 C \xad\xa5 \xa8\xac\xa5\xa5\xe2 \xac\xa5\xe2\xaa\xa8.\r\n \x91\xa5\xe0\xa8\xa9\xad\xeb\xa9 \xad\xae\xac\xa5\xe0 \xe2\xae\xac\xa0: B246-C713\r\n\r\n \x91\xae\xa4\xa5\xe0\xa6\xa8\xac\xae\xa5 \xaf\xa0\xaf\xaa\xa8 C:\\Users\\Lenovo B590\\Documents\\PythonFiles\\SocketKeyLogger\r\n\r\n30.09.2020  13:50    <DIR>          .\r\n30.09.2020  13:50    <DIR>          ..\r\n29.09.2020  16:14                15 .gitignore.txt\r\n30.09.2020  13:40    <DIR>          .idea\r\n29.09.2020  16:55             4\xff306 log.txt\r\n29.09.2020  16:18               321 logger.py\r\n29.09.2020  16:55               157 server_log.txt\r\n30.09.2020  13:50             1\xff980 SockClient.py\r\n29.09.2020  16:55             4\xff160 SockServer.py\r\n29.09.2020  16:55    <DIR>          __pycache__\r\n               6 \xe4\xa0\xa9\xab\xae\xa2         10\xff939 \xa1\xa0\xa9\xe2\r\n               4 \xaf\xa0\xaf\xae\xaa  80\xff338\xff427\xff904 \xa1\xa0\xa9\xe2 \xe1\xa2\xae\xa1\xae\xa4\xad\xae\r\n"

print(b.decode("CP866"))

st = "cd .idea"
print(st[:2])
print(st[3:])