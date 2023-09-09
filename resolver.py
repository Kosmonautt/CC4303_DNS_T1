import binascii
import socket
import funciones_aux as aux
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
    # se transforma el mensaje en esctructura de dnslib
    DNS_structure = DNSRecord.parse(DNS_message)
    # se guarda la ID de la consulta
    DNS_message_ID = DNS_structure.header.id

    # se llama a la función para obtener la response
    response = aux.resolver(DNS_message)

    # se transforma en estructura para cambiar su ID
    response_structure = DNSRecord.parse(response)
    # se cambia su ID
    response_structure.header.id = DNS_message_ID
    # se aplican los cambios a response
    response = bytes(response_structure.pack())

    # se envía la respuesta al cliente
    resolver_socket.sendto(response, client_address)

    print(">>----------------------------------------------<<\n")

    
