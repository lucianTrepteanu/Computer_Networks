# emitator Reliable UDP
from helper_slidingwindow import *
from argparse import ArgumentParser
import socket
import logging
import sys

v=[]
confirm=[]

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

def connect(sock, adresa_receptor):
    '''
    Functie care initializeaza conexiunea cu receptorul.
    Returneaza ack_nr de la receptor si window
    '''
    seq_nr = 0 # TODO: setati initial sequence number
    flags = 'S'
    checksum = 0
    octeti_header_fara_checksum = create_header_emitator(seq_nr, checksum, flags)
    
    mesaj = octeti_header_fara_checksum
    checksum = calculeaza_checksum(mesaj)
    octeti_header_cu_checksum = create_header_emitator(seq_nr, checksum, flags)

    mesaj = octeti_header_cu_checksum

    sock.sendto(mesaj, adresa_receptor)
    
    while True:
        print(mesaj,adresa_receptor)
        sock.sendto(mesaj,adresa_receptor)

        try:
            data, server = sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            # TODO: cat timp nu primește confirmare de connect, incearca din nou
            continue

        if calculeaza_checksum(data)!=0:
            #daca checksum nu e ok, mesajul de la receptor trebuie ignorat
            continue
        
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
    # TODO:
    # folositi pasii de la connect() pentru a construi headerul
    # valorile de checksum si pentru a verifica primirea mesajului a avut loc

    flags='F'
    checksum=0
    octeti_header_fara_checksum=create_header_emitator(seq_nr,checksum,flags)
    
    mesaj=octeti_header_fara_checksum
    checksum=calculeaza_checksum(mesaj)
    octeti_header_cu_checksum=create_header_emitator(seq_nr,checksum,flags)

    mesaj=octeti_header_cu_checksum

    while True:
        sock.sendto(mesaj,adresa_receptor)

        try:
            data,server=sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            continue

        if calculeaza_checksum(data)!=0:
            print('Bad checksum finalize')
            continue

        ack_nr,checksum,window=parse_header_receptor(data)

        logging.info('Ack Nr: "%d"',ack_nr)
        logging.info('Checksum: "%d"',checksum)
        logging.info('Window: "%d"',window)

        return seq_nr  


def send(sock, adresa_receptor, seq_nr, window, octeti_payload):
    '''
    Functie care trimite octeti ca payload catre receptor
    cu seq_nr dat ca parametru.
    Returneaza ack_nr si window curent primit de la server.
    '''
    # TODO...
    flags='P'
    checksum=0
    octeti_header_fara_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload

    mesaj=octeti_header_fara_checksum
    checksum=calculeaza_checksum(mesaj)
    octeti_header_cu_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload

    mesaj=octeti_header_cu_checksum

    while True:
        sock.sendto(mesaj,adresa_receptor)

        try:
            data,server=sock.recvfrom(MAX_SEGMENT)
        except socket.timeout as e:
            logging.info("Timeout la connect, retrying...")
            continue

        if calculeaza_checksum(data)!=0:
            print('Bad checksum')
            continue

        ack_nr,checksum,window=parse_header_receptor(data)

        logging.info('Ack Nr: "%d"', ack_nr)
        logging.info('Checksum: "%d"', checksum)
        logging.info('Window: "%d"', window)

        return ack_nr, window


def construct_mesaj(seq_nr,flags,octeti_payload):
    checksum=0
    octeti_header_fara_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload
    mesaj=octeti_header_fara_checksum
    
    checksum=calculeaza_checksum(mesaj)
    octeti_header_cu_checksum=create_header_emitator(seq_nr,checksum,flags)+octeti_payload
    mesaj=octeti_header_cu_checksum
    
    return mesaj

def send_window(sock,adresa_receptor,seq_nr,window,pos):
    final_ack_nr=0
    flag=True

    while flag is True:
        for i in range(WINDOW_SIZE):
            try:
                logging.info("Trimitem pachetul ..",i)
                mesaj=construct_mesaj(seq_nr,'P',v[pos+i])
                sock.sendto(mesaj,adresa_receptor)
                data,server=sock.recvfrom(MAX_SEGMENT)

                if calculeaza_checksum(data)!=0:
                    logging.info('Bad checksum')
                    flag=True
                    ack_nr,checksum,window=parse_header_receptor(data)
                    final_ack_nr=max(final_ack_nr,ack_nr)
                else:
                    to_send[i]=False
            except:
                logging.info("Timeout la connect, retrying...")
                flag=True

    return final_ack_nr,window


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
    sock.settimeout(0.3)

    ack_nr, window = connect(sock, adresa_receptor)
    file_descriptor = open(fisier, 'rb')
    
    ## TODO: send trebuie sa trimită o fereastră de window segmente
    # până primșete confirmarea primirii tuturor segmentelor
    b=bytes()
    while True:
        b=file_descriptor.read(BUFFER_SIZE)
        if len(b)<1:
            break
        v.append(b)

    n=len(v)
    confirm=[False for i in range(n)]
    left=0
    while left<n:
        cnt=0
        for i in range(left,min(left+WINDOW_SIZE,n)):
            if confirm[i] is False:
                cnt=cnt+1
                logging.info('Trimitem pachetul .."%d" din "%d"',i,n)
                mesaj=construct_mesaj(i,'P',v[i])
                sock.sendto(mesaj,adresa_receptor)

        while True:
            if cnt<=0:
                break
            try:
                data,server=sock.recvfrom(MAX_SEGMENT)
                ack_nr,checksum,window=parse_header_receptor(data)
                print("Am primit pachetul cu nr ",ack_nr)

                confirm[ack_nr]=True
                cnt=cnt-1
            except socket.timeout as e:
                logging.info("Timeout la connect, retrying...")
                break

        while left<n and confirm[left] is True:
            left=left+1

    finalize(sock,adresa_receptor,ack_nr)
    sock.close()
    file_descriptor.close()


if __name__ == '__main__':
    main()