import socket
import os
import struct

s = socket.socket()
print(s)
REMOTE_IP_PORT = ('127.0.0.1', 5467)
LOCAL_IP_PORT = ('127.0.0.1', 5468)
# s.bind(LOCAL_IP_PORT)
s.connect(REMOTE_IP_PORT)

while True:
    req_method = 'post'
    image = 'test_image/1483351.jpg'
    file_name = os.path.basename(image)
    file_size = os.stat(image).st_size
    file_info = struct.pack('l', file_size)
    s.sendall(file_info)
    # print('client file size:', file_size)
    # s.sendall(bytes(str(file_size), 'utf8'))

    file = open(image, 'rb')
    sent_size = 0
    while sent_size != file_size:
        data = file.read(1024)
        s.sendall(data)
        sent_size += len(data)
    file.close()
    print('Upload successfully.')
    resp_size = struct.calcsize('l')
    label_result = s.recv(resp_size)
    label_result = struct.unpack('l', label_result)[0]
    print('response label:', label_result)
    break
