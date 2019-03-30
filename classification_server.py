import socket
import os
import time
import threading
import struct
import hashlib
from image_classification import do_classification, ERR_CANNOT_IDENTIFY_IMAGE

ERR_TIMEOUT_WHILE_RECV_DATA = -2
ERR_MD5_INCONSISTENT = -3
ERR_UNKNOWN_FILE_INFO = -4
ERR_TIMEOUT_WHILE_RECV_INFO = -5
s = socket.socket()
print(socket)
IP_PORT = ('127.0.0.1', 5467)
s.bind(IP_PORT)
s.listen(1)


def conn_thread(connection):
    try:
        connection.settimeout(40)
        file_info_size = struct.calcsize('l32s')
        # print('[server]', file_info_size)
        data = connection.recv(file_info_size)  # 第一次接收待接收文件信息
        try:
            file_size, md5 = struct.unpack('l32s', data)
            md5 = str(md5, encoding='utf8')
            print('[server] file size:', file_size, ', md5:', md5)
        except Exception as e:
            print(e)
            server_msg = 'Unpackable file info. ' \
                         'Please send the file information in a structure format of ' \
                         '{file size (int, 4 bytes); MD5 (32 bytes encoded in utf8)}.'
            resp = struct.pack('l256s', ERR_UNKNOWN_FILE_INFO, bytes(server_msg, 'utf8'))
            connection.sendall(resp)
            connection.close()
            return
        server_msg = 'Server is ready to receive a %d bytes image file.' % file_size
        resp = struct.pack('l256s', 0, bytes(server_msg, 'utf8'))
        connection.sendall(resp)

        file_name = str(time.time()).replace('.', '')
        file_path = os.path.join('image', file_name)
        file = open(file_path, 'ab')
        connection.settimeout(10)
        try:
            received_size = 0
            while received_size != file_size:  # 第二次接收，开始接收文件数据
                data = connection.recv(1024)
                file.write(data)
                received_size += len(data)
            print('[server] File', file_path, 'has been successfully downloaded.')
        except socket.timeout as e:
            print(e)
            server_msg = 'Server received a file_size value of ' + str(file_size) + \
                         ', but timed out while receiving file data.'
            resp = struct.pack('l256s', ERR_TIMEOUT_WHILE_RECV_DATA, bytes(server_msg, 'utf8'))
            connection.sendall(resp)
            # print('[server] response sent')
            connection.close()
            file.close()
            os.remove(file_path)
            return
        finally:
            file.close()

        # 比较文件md5是否一致
        with open(file_path, 'rb') as file:
            received_md5 = hashlib.md5(file.read()).hexdigest()
        print('[server] received md5: ' + received_md5)
        if received_md5 != md5:
            result_label = ERR_MD5_INCONSISTENT
        else:
            result_label = do_classification(file_path)

        if result_label == 0:
            server_msg = '(idr0008_rohn_actinome_screenA)'
        elif result_label == 1:
            server_msg = '(idr0009_simpson_secretion_screenA)'
        elif result_label == 2:
            server_msg = '(idr0010_doil_dnadamage_screenA)'
        elif result_label == 3:
            server_msg = '(idr0013_neumann_mitocheck_screenA)'
        elif result_label == 4:
            server_msg = '(idr0035_caie_drugresponse_screenA)'
        elif result_label == ERR_CANNOT_IDENTIFY_IMAGE:
            server_msg = 'Cannot identify image, the image file may be damaged.'
        elif result_label == ERR_MD5_INCONSISTENT:
            server_msg = 'The MD5 of files are inconsistent.'
        else:
            server_msg = 'Unknown error!'
        resp = struct.pack('l256s', result_label, bytes(server_msg, 'utf8'))
        connection.sendall(resp)
        connection.close()
        print('result label is', result_label)
        os.remove(file_path)
    except socket.timeout as e1:
        print(e1)
        server_msg = 'Server timed out while receiving file info.'
        resp = struct.pack('l256s', ERR_TIMEOUT_WHILE_RECV_INFO, bytes(server_msg, 'utf8'))
        connection.sendall(resp)
        connection.close()
    except socket.error as e2:
        print(e2)


while True:
    conn, addr = s.accept()
    print('connected by:', addr)
    thread = threading.Thread(target=conn_thread, args=(conn,))
    thread.start()
