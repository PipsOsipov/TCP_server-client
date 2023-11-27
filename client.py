import os
import signal
import socket


def handler(signum, frame):
    raise Exception("Время ожидания истекло")


# Установка обработчика сигнала
signal.signal(signal.SIGABRT, handler)


def start_client(host='192.168.0.16', port=1234):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    while True:
        msg = input("Введите команду: ")
        command = msg.split(' ')[0]
        client.send(msg.encode('utf-8'))
        if command.lower() in ["close", "exit", "quit"]:
            break
        elif command.lower() == "upload":
            filename = ' '.join(msg.split(' ')[1:])
            upload_path = 'C:\\Client'  # Введите путь откуда загрузить файл
            try:
                with open(os.path.join(upload_path, filename), 'rb') as file:
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        client.send(data)
                print(f"Файл {filename} успешно отправлен.")
            except FileNotFoundError:
                print("Файл не найден.")
        elif command.lower() == "download":
            filename = ' '.join(msg.split(' ')[1:])
            download_path = 'C:\\servDownload'  # Введите путь для сохранения файла
            with open(os.path.join(download_path, filename), 'ab') as file:  # Открываем файл для дозаписи
                client.send(str(file.tell()).encode('utf-8'))  # Отправляем серверу текущую позицию в файле
                while True:
                    data = client.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print(f"Файл {filename} успешно загружен в {download_path}.")
        else:
            response = client.recv(1024).decode('utf-8')
            print(response)
    client.close()


start_client()
