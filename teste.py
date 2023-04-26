import socket

host = 'gwqa.revolog.com.br'
port = 1884

addr_info = socket.getaddrinfo(host, port)
print(addr_info)
