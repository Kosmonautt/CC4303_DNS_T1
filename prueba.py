import random

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



        



                


cache1 = Cache()

for i in range(0,25):
    j = random.randint(1,10)

    cache1.add_to_last20(('vaina{}'.format(j), '1.1.1.{}'.format(j)))

cache1.setfiveMostRepeated()

print(cache1.fiveMostRepeated)








