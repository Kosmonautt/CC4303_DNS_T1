import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

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
    # se guardan en una lista
    sections = [Answer, Authority, Additional]

    return (Qname, counts, sections)

