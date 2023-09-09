import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

# ip del servidor raíz
ip_root = "192.33.4.12"

# función que transforma un mensaje DNS en una estrcutura manejable
def parse_DNS_message(DNS_mssg):
    # se parsea con dnslib
    DNS_mssg = DNSRecord.parse(DNS_mssg)

    # primer objeto en la lista all_querys
    first_query = DNS_mssg.get_q()  

    # se guarda el nombre del sitio que se busca
    Qname = first_query.get_qname()

    # se guarda QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT
    QDCOUNT = DNS_mssg.header.q
    ANCOUNT = DNS_mssg.header.a
    NSCOUNT = DNS_mssg.header.auth
    ARCOUNT = DNS_mssg.header.ar
    # se guardan en una lista
    counts = [QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT]

    # se guarda la sección de Answer, Authority y Additional
    Answer = DNS_mssg.rr
    Authority = DNS_mssg.auth
    Additional = DNS_mssg.ar
    # se guardan en una listaroot_response
    sections = [Answer, Authority, Additional]

    return [Qname, counts, sections]

# función que le manda un mensaje DNS a cierta dirección y retorna la respuesta
def send_dns_message(qname ,address, port):
     # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
     q = DNSRecord.question(qname)
     server_address = (address, port)
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     try:
         # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
         sock.sendto(bytes(q.pack()), server_address)
         # En data quedará la respuesta a nuestra consulta
         response, _ = sock.recvfrom(4096)
     finally:
         sock.close()
     return response

# función recursiva que da el resultado de una query
def resolver_recursive(qname, ip):


    print("(debug) Consultando {} a dirección IP {}".format(qname, ip))


    # se hace la request a la dirección ip con el nombre del sitio buscado
    response = send_dns_message(qname, ip, 53)
    # se transforma la response en una estrcutura
    response_struct = parse_DNS_message(response)
    # se consigue la estructura con los "counts"
    counts = response_struct[1]
    # se consigue la estructura con las "sections"
    sections = response_struct[2]

    # si es que hay answers
    if counts[1] > 0:
        # se consiguen Answers
        Answers = sections[0]

        # para cada RR 
        for i in range(0,counts[1]):
            # se consigue la RR
            answer = Answers[i]
            # se consigue el tipo de la RR
            answer_type = QTYPE.get(answer.rtype)
            # si el tipo de RR es A, se retorna la response
            if answer_type == 'A':
                return response
            
    # si vienen authority records (NS)
    if counts[2] >0:
        # se consigue Aditional
        Additional = sections[2]

        # para cada RR en Additional
        for i in range(0,counts[3]):
            # se consigue la RR
            add_rr = Additional[i]
            # se consigue el tipo de la RR
            add_rr_type = QTYPE.get(add_rr.rtype)
            # si el tipo de RR es A
            if add_rr_type == 'A':                
                # se consigue la Rdata con la ip
                add_rr_ip = str(add_rr.rdata)
                # se retorna recursivamente
                return resolver_recursive(qname, add_rr_ip)

        # si no se encuetra en Additional
        # se consigue Authority
        Authority = sections[1]

        # para cada RR en Authority
        for i in range(0, counts[2]):
            # se consigue la RR
            auth_rr = Authority[i]
            # se consigue el name server
            auth_rr_name = auth_rr.rname
            # se llama recursivamente para obtener la IP del name server
            auth_response = resolver_recursive(auth_rr_name,ip_root)
            # una vez obtenida la response se transforma en estrcutura
            auth_struct = parse_DNS_message(auth_response)
            # se consigue Answer
            auth_Answer = auth_struct[2][0]
            # se consigue la primera RR
            auth_first_rr = auth_Answer.get_a()
            # se consigue su ip asociada
            auth_ip = str(auth_first_rr.rdata)

            # se llama recursivamente
            return resolver_recursive(response_struct[0], auth_ip) 
        
        


    




# función que recibe una query en bytes del cliente e intenta devolver el resultado adecuado
def resolver(DNS_mssg):
    # se transforma en una estructura manejable el sitio que quiere el usuario
    client_structure = parse_DNS_message(DNS_mssg)
    # se consigue el sitio que quiere el cliente
    client_request_name = client_structure[0]

    # se le hace la consulta a la raíz
    return resolver_recursive(client_request_name, ip_root)



