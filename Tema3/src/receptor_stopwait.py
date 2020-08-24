# receptor Reiable UDP
from helper_stopwait import *
from argparse import ArgumentParser
import socket
import logging

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

last_seq_nr={}
def append_to_file(file_path,data):
    with open(file_path,"ab") as f:
        f.write(data)

def main():
    parser = ArgumentParser(usage=__file__ + ' '
                                             '-p/--port PORT'
                                             '-f/--fisier FILE_PATH',
                            description='Reliable UDP Receptor')

    parser.add_argument('-p', '--port',
                        dest='port',
                        default='10000',
                        help='Portul pe care sa porneasca receptorul pentru a primi mesaje')

    parser.add_argument('-f', '--fisier',
                        dest='fisier',
                        help='Calea catre fisierul in care se vor scrie octetii primiti')

    # Parse arguments
    args = vars(parser.parse_args())
    port = int(args['port'])
    fisier = args['fisier']

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

    adresa = '0.0.0.0'
    server_address = (adresa, port)
    sock.bind(server_address)
    logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)

    while True:
        logging.info('Asteptam mesaje...')
        data, address = sock.recvfrom(MAX_SEGMENT)
        '''
        TODO: pentru fiecare mesaj primit
        1. verificam checksum
        2. parsam headerul de la emitator
        3. trimitem confirmari cu ack = seq_nr+1 daca mesajul e de tip S sau F
                               cu ack = seq_nr daca mesajul e de tip P
        4. scriem intr-un fisier octetii primiti
        5. verificam la sfarsit ca fisierul este la fel cu cel trimis de emitator
        '''

        seq_nr, checksum, flags=parse_header_emitator(data[:8])
        if calculeaza_checksum(data)!=0:
            print('Bad checksum')
            continue

        payload=data[8:]
        if flags is 'S':
            checksum=0
            octeti_header_fara_checksum=create_header_emitator(seq_nr+1,checksum,flags)

            mesaj=octeti_header_fara_checksum
            checksum=calculeaza_checksum(mesaj)
            octeti_header_cu_checksum=create_header_emitator(seq_nr+1,checksum,flags)

            mesaj=octeti_header_cu_checksum
            sock.sendto(mesaj,address)
        elif flags is 'F':
            checksum=0
            octeti_header_fara_checksum=create_header_emitator(seq_nr,checksum,flags)

            mesaj=octeti_header_fara_checksum
            checksum=calculeaza_checksum(mesaj)
            octeti_header_cu_checksum=create_header_emitator(seq_nr,checksum,flags)

            mesaj=octeti_header_cu_checksum
            sock.sendto(mesaj,address)
        else:
            checksum=0
            octeti_header_fara_checksum=create_header_emitator(seq_nr+1,checksum,flags)

            mesaj=octeti_header_fara_checksum
            checksum=calculeaza_checksum(mesaj)
            octeti_header_cu_checksum=create_header_emitator(seq_nr+1,checksum,flags)

            mesaj=octeti_header_cu_checksum
            if seq_nr not in last_seq_nr:
                append_to_file(fisier,payload)
                last_seq_nr[seq_nr]=1
            sock.sendto(mesaj,address)

if __name__ == '__main__':
    main()

