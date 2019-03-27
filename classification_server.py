import socket
import os
import time
import threading
import struct
from image_classification import do_classification

s = socket.socket()
print(socket)
IP_PORT = ('127.0.0.1', 5467)
s.bind(IP_PORT)
s.listen(1)


def conn_thread(conn):
    try:
        conn.settimeout(600)
        file_info_size = struct.calcsize('l')
        data = conn.recv(file_info_size)  # 第一次接收待接收文件信息
        if data or True:
            file_size = struct.unpack('l', data)[0]
            print('server file size:', file_size)
            file_name = str(time.time()).replace('.', '')
            file_path = os.path.join('image', file_name)

            file = open(file_path, 'ab')
            received_size = 0
            while received_size != file_size:  # 第二次接收，开始接收文件数据
                data = conn.recv(1024)
                file.write(data)
                received_size += len(data)
            file.close()
            # conn.close()
            result_label = do_classification(file_path)
            resp = struct.pack('l', result_label)
            conn.sendall(resp)
            print('image is belong to label', result_label)
    except socket.error as e:
        print(e)


while True:
    print('waiting...')
    conn, addr = s.accept()
    print('connected by:', addr)
    thread = threading.Thread(target=conn_thread, args=(conn,))
    thread.start()
