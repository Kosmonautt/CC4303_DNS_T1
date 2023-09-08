import binascii
import socket
import funciones_aux as aux

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
    DNS_message, _ = resolver_socket.recvfrom(buff_size)
    # se transoforma la data en una estrcutura
    structure = aux.parse_DNS_message(DNS_message)
    print(structure)