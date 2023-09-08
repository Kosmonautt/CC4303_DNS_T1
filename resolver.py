import binascii
import socket

# puerto donde funicionará el server
port = 8000
# tamaño del buffer
buff_size = 4096
# dirección del resolver
resolver_adress = ('localhost', port)
# se crea el resolver (no orientado a conexión)
resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# se asocia a su dirección
resolver_socket.bind(resolver_adress)

# se deja "corriendo" el server
while True:
    # se guarda la data reibida
    data, _ = resolver_socket.recvfrom(buff_size)
    # se imprime la data reibida
    print(data)