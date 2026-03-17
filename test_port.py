import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(s.connect_ex(('127.0.0.1', 8000)))
