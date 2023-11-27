import signal
import socket
import threading
import time
import os

file_info = {}


def start_server(host='192.168.187.149', port=1234):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print("Сервер запущен...")
    while True:
        conn, address = server.accept()
        conn.settimeout(150)  # Установка таймаута на 60 секунд
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()
        # handle_client(conn, address)


def handle_client(conn, address):
    print(f"Новое подключение: {address}")
    connected = True
    while connected:
        try:
            msg = conn.recv(4096).decode('utf-8')
        except socket.timeout:
            print("Время ожидания истекло")
            break
        command = msg.split(' ')[0]
        if command.lower() == "echo":
            conn.send(msg.encode('utf-8'))
        elif command.lower() == "time":
            conn.send(time.ctime(time.time()).encode('utf-8'))
        elif command.lower() == "upload":
            filename = ' '.join(msg.split(' ')[1:])
            upload_path = 'C:\\Client'  # Введите путь для сохранения файла
            with open(os.path.join(upload_path, filename), 'wb') as file:
                file_size = os.path.getsize(os.path.join(upload_path, filename))
                while True:
                    try:
                        data = conn.recv(4096)
                    except socket.error:
                        print(f"Файл {filename} успешно загружен в {upload_path}. Размер файла {file_size} байт")
                        break
                    if not data:
                        break
                    file.write(data)
            file_info[filename] = file_size
        elif command.lower() == "download":
            filename = ' '.join(msg.split(' ')[1:])
            download_path = 'C:\\server'  # Введите путь откуда скачать файл
            try:
                with open(os.path.join(download_path, filename), 'rb') as file:
                    file.seek(int(conn.recv(4096).decode('utf-8')))  # Переходим к месту разрыва
                    while True:
                        data = file.read(4096)
                        if not data:
                            break
                        conn.send(data)
                file_size = os.path.getsize(os.path.join(download_path, filename))
                print(f"Файл {filename} успешно отправлен. Размер файла {file_size} байт")
                file_info[filename] = file_size
            except FileNotFoundError:
                print("Файл не найден.")
                conn.send("Файл не найден")
        elif command.lower() == "info":
            # Отправляем информацию о файлах
            for filename, size in file_info.items():
                conn.send(f"Файл: {filename}, Размер: {size} байт.\n".encode('utf-8'))
        elif command.lower() in ["close", "exit", "quit"]:
            connected = False
    conn.close()


start_server()
