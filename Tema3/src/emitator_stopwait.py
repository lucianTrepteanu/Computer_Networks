# emitator Reliable UDP
from helper_stopwait import *
from argparse import ArgumentParser
import socket
import logging
import sys

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

def connect(sock, adresa_receptor):
    '''
    Functie care initializeaza conexiunea cu receptorul.
    Returneaza ack_nr de la receptor si window
    '''
    seq_nr = 0
    flags = 'S'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr, checksum, flags)
    
    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr, checksum, flags)

    mesaj = octeti_header_cu_checksum

    while True:
        #print(mesaj,adresa_receptor)
        sock.sendto(mesaj, adresa_receptor)
    
        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            continue
            # TODO: cat timp nu primește confirmare de connect, incearca din nou

        if calculeaza_checksum(data) !=0:
            #daca checksum nu e ok, mesajul de la receptor trebuie ignorat
            print('Bad checksum')
            continue
            #return -1, -1
    
    ack_nr, checksum, window = parse_header_receptor(data)

    logging.info('Ack Nr: "%d"', ack_nr)
    logging.info('Checksum: "%d"', checksum)
    logging.info('Window: "%d"', window)

    return ack_nr, window


def finalize(sock, adresa_receptor, seq_nr):
    '''
    Functie care trimite mesajul de finalizare
    cu seq_nr dat ca parametru.
    '''

    flags = 'F'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr, flags, checksum)
    
    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr, flags, checksum)

    mesaj = octeti_header_cu_checksum

    while True:
        sock.sendto(mesaj, adresa_receptor)
    
        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            continue

        if calculeaza_checksum(data) !=0:
            #daca checksum nu e ok, mesajul de la receptor trebuie ignorat
            print('Bad checksum')
            continue
            #return -1, -1
    
    ack_nr, checksum, window = parse_header_receptor(data)

    logging.info('Ack Nr: "%d"', ack_nr)
    logging.info('Checksum: "%d"', checksum)
    logging.info('Window: "%d"', window)

    # TODO:
    # folositi pasii de la connect() pentru a construi headerul
    # valorile de checksum si pentru a verifica primirea mesajului a avut loc

    return seq_nr


def send(sock, adresa_receptor, seq_nr, window, octeti_payload):
    '''
    Functie care trimite octeti ca payload catre receptor
    cu seq_nr dat ca parametru.
    Returneaza ack_nr si window curent primit de la server.
    '''

    flags = 'P'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr, flags, checksum) + octeti_payload
    
    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr, flags, checksum)+octeti_payload

    mesaj = octeti_header_cu_checksum

    while True:
        sock.sendto(mesaj, adresa_receptor)
    
        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            continue
        
        if calculeaza_checksum(data) !=0:
            #daca checksum nu e ok, mesajul de la receptor trebuie ignorat
            print('Bad checksum')
            continue
            #return -1, -1
    
        ack_nr, checksum, window = parse_header_receptor(data)

        logging.info('Ack Nr: "%d"', ack_nr)
        logging.info('Checksum: "%d"', checksum)
        logging.info('Window: "%d"', window)

    return ack_nr, window

def send_window(sock,adresa_receptor,seq_nr,window,octeti_payload):
    '''
    Functie care trimite octeti ca payload catre receptor
    cu seq_nr dat ca parametru.
    Returneaza ack_nr si window curent primit de la server.
    '''
    flags='P'
    checksum=0
    octeti_header_fara_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload

    mesaj=octeti_header_fara_checksum
    checksum=calculeaza_checksum(mesaj)
    octeti_header_cu_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload
    
    mesaj=octeti_header_cu_checksum
    sock.sendto(mesaj,adresa_receptor)

def main():
    parser = ArgumentParser(usage=__file__ + ' '
                                             '-a/--adresa IP '
                                             '-p/--port PORT'
                                             '-f/--fisier FILE_PATH',
                            description='Reliable UDP Emitter')

    parser.add_argument('-a', '--adresa',
                        dest='adresa',
                        default='receptor',
                        help='Adresa IP a receptorului (IP-ul containerului, localhost sau altceva)')

    parser.add_argument('-p', '--port',
                        dest='port',
                        default='10000',
                        help='Portul pe care asculta receptorul pentru mesaje')

    parser.add_argument('-f', '--fisier',
                        dest='fisier',
                        help='Calea catre fisierul care urmeaza a fi trimis')

    # Parse arguments
    args = vars(parser.parse_args())

    ip_receptor = args['adresa']
    port_receptor = int(args['port'])
    fisier = args['fisier']

    adresa_receptor = (ip_receptor, port_receptor)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    # setam timeout pe socket in cazul in care recvfrom nu primeste nimic in 3 secunde
    sock.settimeout(3)
    ack_nr, window = connect(sock, adresa_receptor)
    file_descriptor = open(fisier, 'rb')

    while True:
        b=file_descriptor.read(BUFFER_SIZE)
        print(b)
        if len(b)<1:
            break
        ack_nr,window=send(sock,adresa_receptor,ack_nr,window,b)

    finalize(sock,adresa_receptor,ack_nr)
    sock.close()
    file_descriptor.close()


if __name__ == '__main__':
    main()