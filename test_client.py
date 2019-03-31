import socket
import os
import struct
import hashlib

s = socket.socket()
print(s)
ERR_CANNOT_IDENTIFY_IMAGE = -1
ERR_TIMEOUT_WHILE_SEND_DATA = -2
ERR_UNKNOWN_FILE_INFO = -4
REMOTE_IP_PORT = ('127.0.0.1', 5467)
# LOCAL_IP_PORT = ('127.0.0.1', 5468)
# s.bind(LOCAL_IP_PORT)
s.connect(REMOTE_IP_PORT)

while True:
    req_method = 'post'
    image = 'test_image/idr0009a_1.png'
    file_name = os.path.basename(image)
    file_size = os.stat(image).st_size

    file = open(image, 'rb')
    # 计算文件MD5值
    md5 = hashlib.md5(file.read()).hexdigest()
    print('[client] md5: ' + md5)
    file.close()

    # 打包发送文件大小及MD5信息
    file_info = struct.pack('l32s', file_size, bytes(md5, 'utf8'))
    s.sendall(file_info)
    resp_size = struct.calcsize('256s')
    server_resp = s.recv(resp_size)
    server_msg = struct.unpack('256s', server_resp)[0]
    server_msg = str(server_msg, encoding='utf8')
    resp_code = server_msg[23]
    # print('resp_code: ', resp_code)
    print(server_msg)
    if resp_code != '0':
        break

    file = open(image, 'rb')
    sent_size = 0
    while sent_size != file_size:
        data = file.read(1024)
        s.sendall(data)
        sent_size += len(data)
    file.close()
    print('Upload successfully.')
    resp_size = struct.calcsize('256s')
    server_resp = s.recv(resp_size)
    server_msg = struct.unpack('256s', server_resp)[0]
    server_msg = str(server_msg, encoding='utf8')
    print('[client] Server message:', server_msg)
    # print('[client] label result:', label_result)
    # if label_result == ERR_TIMEOUT_WHILE_SEND_DATA:
    #     print(server_msg.strip())
    #     print('请注意上传数据的格式。')
    # elif label_result == ERR_CANNOT_IDENTIFY_IMAGE:
    #     print(server_msg.strip())
    # else:
    #     print('classification label:', label_result, server_msg)
    break
