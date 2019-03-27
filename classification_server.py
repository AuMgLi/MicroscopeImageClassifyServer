import socket
import os
import time
from image_classification import do_classification

socket = socket.socket()
print(socket)
IP_PORT = ('127.0.0.1', 5467)
socket.bind(IP_PORT)
socket.listen(3)
print('waiting...')

while True:
    conn, addr = socket.accept()  # 第一次接收待接收文件信息
    data = conn.recv(1024)
    file_size = int(str(data, 'utf8'))
    file_name = str(time.time()).replace('.', '')
    file_path = os.path.join('image', file_name)

    file = open(file_path, 'ab')
    received_size = 0
    while received_size != file_size:  # 第二次接收，开始接收文件数据
        data = conn.recv(1024)
        file.write(data)
        received_size += len(data)
    file.close()
    print('image is belong to label', do_classification(file_path))
    print('waiting...')
