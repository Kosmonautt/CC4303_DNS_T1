import binascii
import socket
import funciones_aux_2 as aux
import test
from dnslib import DNSRecord


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
    # se guarda la data reibida y la dirección del cliente
    DNS_message, client_address = resolver_socket.recvfrom(buff_size)

    # se llama a la función para obtener la response
    response = aux.resolver(DNS_message)

    # se envía la respuesta al cliente
    resolver_socket.sendto(response, client_address)

    print(">>----------------------------------------------<<\n")
