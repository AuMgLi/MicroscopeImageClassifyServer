import socket
import os

socket = socket.socket()
print(socket)
address = ('127.0.0.1', 5467)
socket.connect(address)
# BASE_DIR

while True:
    req_method = 'post'
    image = 'test_image/35995.jpg'
    file_name = os.path.basename(image)
    file_size = os.stat(image).st_size
    # print('file name:', file_name, ', file size:', file_size)
    # file_info = req_method + '|' + file_name + '|' + str(file_size)
    # print(file_info)
    socket.sendall(bytes(str(file_size), 'utf8'))

    file = open(image, 'rb')
    sent_size = 0
    while sent_size != file_size:
        data = file.read(1024)
        socket.sendall(data)
        sent_size += len(data)
    file.close()
    print('Upload successfully.')
    break
