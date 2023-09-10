import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, A
from dnslib.dns import QTYPE

# ip del servidor raíz
ip_root = "192.33.4.12"

# clase caché
class Cache:
    def __init__(self):
        self.fiveMostRepeated = {}
        self.last20 = []
    
    # función que añade un par (dominio, ip) a la lista
    def add_to_last20(self, domain_ip_pair):
        # si la lista tiene más de 20 elementos
        if len(self.last20) >= 20:
            # se remueve el primero (más antiguo)
            self.last20.pop(0)
            # se añade el nuevo
            self.last20.append(domain_ip_pair)
        # si no 
        else:
            # se añade el nuevo
            self.last20.append(domain_ip_pair)
    
    # función que configura los últimos 5 domnios más visitados dados los último 20
    def setfiveMostRepeated(self):
        # se reinicia el dicc de 5 más repetidos
        self.fiveMostRepeated = {}

        # diccionario con llave el pair (dominio, ip) y valor la cantidad de veces que se repite en la lista
        # self.last20
        ocurrences = {}
        # para cada par en la lista
        for p in self.last20:
            # si ya está en ocurrences 
            if p in ocurrences:
                # se aumenta en 1
                ocurrences[p] += 1
            # si no está
            else:
                # se añade con solo un elemento
                ocurrences.update({p:1})

        # se ordena por ocurrencias en orden decreciente
        ocurrences = dict(sorted(ocurrences.items(), key = lambda x: x[1], reverse=True))

        # se recorre el dicc ordenado para agregar a los 5 más repetidos
        for key, value in ocurrences.items():
            # se añade a los 5 más repetidos
            self.fiveMostRepeated.update({key[0]:key[1]})
            # si se llegó a 5
            if len(self.fiveMostRepeated) >=5:
                # se sale del for
                break

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
def send_dns_message(query ,address, port):
    # se guarda la dirección donde se quiere enviar la query
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # enviamos el mensaje a la dirección dada
        sock.sendto(query, server_address)
        # En data quedará la respuesta a nuestra consulta
        response, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    # se retorna la response a la query
    return response

# función recursiva que da el resultado de una query
def resolver(query, ip, ipName, cache, debug=False):
    # se transofrma la query en una estrcutura manejable
    query_structure = parse_DNS_message(query)
    # se consigue el nombre del sitio deseado
    qname = query_structure[0]
    # se pasa a str
    qname = str(qname)
    
    # si está en el caché
    if qname in cache.fiveMostRepeated:
        if debug:
            print("(debug) Consultando '{}' a el Cache".format(qname))
        # se consigue la ID de la pregunta
        ID = (DNSRecord.parse(query)).header.id
        #print(ID)

        return response_cache(ID, qname, cache.fiveMostRepeated[qname])

    if debug:
        # se imprime el debug
        print("(debug) Consultando '{}' a '{}' con dirección IP '{}'".format(qname,ipName,ip))

    # se hace la request a la dirección ip con la query dada 
    response = send_dns_message(query, ip, 53)
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
            # si el tipo de RR es A
            if answer_type == 'A':
                # se añadé la dirección al caché 
                cache.add_to_last20((qname,str(answer.rdata)))
                # se actualiza el caché
                cache.setfiveMostRepeated()
                # se retorna la response
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
                # se consigue el nombre del dominio
                add_rr_name = add_rr.get_rname()              
                # se consigue la Rdata con la ip
                add_rr_ip = str(add_rr.rdata)
                # se retorna recursivamente
                return resolver(query, add_rr_ip, add_rr_name, cache, debug)

        # si no se encuetra en Additional
        # se consigue Authority
        Authority = sections[1]

        # para cada RR en Authority
        for i in range(0, counts[2]):
            # se consigue la RR
            auth_rr = Authority[i]
            # se consigue el name server (desde su parte de rdata)
            auth_rr_name = str(auth_rr.rdata)
            # se crea un query con el nombre de la RR
            autrh_rr_query = DNSRecord.question(auth_rr_name)
            # se pasa a bytes
            autrh_rr_query = bytes(autrh_rr_query.pack())
            # se llama recursivamente para obtener la IP del name server
            auth_response = resolver(autrh_rr_query,ip_root, ".", cache, debug)
            # una vez obtenida la response se transforma en estructura de dnslib
            auth_Answer = DNSRecord.parse(auth_response)
            # se consigue la primera respuesta de answer
            auth_first_rr = auth_Answer.get_a()
            # se consigue su ip asociada
            auth_ip = str(auth_first_rr.rdata)
            # se consigue su nombre
            auth_name = str(auth_first_rr.rname)
            # se añadé la dirección al caché 
            cache.add_to_last20((auth_name,auth_ip))
            # se actualiza el caché
            cache.setfiveMostRepeated()  

            # se llama recursivamente
            return resolver(query, auth_ip, auth_name, cache, debug) 
        
# función que retorna una response a una query dando el ID de la query, el nombre del sitio buscado, y su ip

def response_cache(qID, qname, qIP):
    # se crea una response con el nombre del dominio, la IP
    d = DNSRecord(DNSHeader(qr=1,aa=1,ra=1),
                            q=DNSQuestion(qname),
                            a=RR(qname,rdata=A(qIP)))
    # se cambia la ID en el header
    d.header.id = qID
    # se retorna en bytes
    return bytes(d.pack())


