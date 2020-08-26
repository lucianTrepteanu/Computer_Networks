# Tema 5

## Informații temă
**Deadline**: **25 iunie 2020** 

Pentru a vă înscrie folosiți acest link: [https://classroom.github.com/g/32uTw0NR](https://classroom.github.com/g/32uTw0NR).

Tema se va rezolva în echipe de maxim două persoane iar punctajul temei este 10% din nota finală.
Veți fi evaluați individual în funcție de commit-uri în repository prin `git blame` și `git-quick-stats -a`. Doar utilizatorii care apar cu modificări în repository vor fi punctați (în funcție de modificările pe care le fac).

### Barem
Predați cod și mesaje de logging în [Rezolvare.md](https://github.com/senisioi/tema5/blob/master/Rezolvare.md) pentru
1. ARP Spoofing - 5% 
2. TCP Hijacking - 5% 

### Observații
1. E posibil ca tabelel ARP cache ale containerelor `router` și `server` să se updateze mai greu. Ca să nu dureze câteva ore până verificați că funcționează, puteți să le curățați în timp ce sau înainte de a declanșa atacul folosind [comenzi de aici](https://linux-audit.com/how-to-clear-the-arp-cache-on-linux/)
2. Orice bucată de cod pe care o luați de pe net trebuie însoțită de comments în limba română, altfel nu vor fi punctate.
3. Atacurile implementante aici au un scop didactic, nu încercați să folosiți aceste metode pentru a ataca alte persoane de pe o rețea locală.


### Structura containerelor
Tema 5 conține aceeași structură de container ca în capitolul3. Pentru a construi containerele, rulăm `docker-compose up -d`.
Imaginea este construită pe baza fișierul `Dockerfile-tema5`, dacă facem modificări în fișier sau în scripturile shell, putem rula `docker-compose build --no-cache` pentru a reconstrui imaginile containerelor.


## 1. ARP Spoofing (5%)
[ARP spoofing](https://samsclass.info/124/proj11/P13xN-arpspoof.html) presupune trimiterea unui pachet ARP de tip reply către o țintă pentru a o informa greșit cu privire la adresa MAC pereche pentru un IP. [Aici](https://medium.com/@ismailakkila/black-hat-python-arp-cache-poisoning-with-scapy-7cb1d8b9d242) și [aici](https://www.youtube.com/watch?v=hI9J_tnNDCc) puteți urmări cum se execută un atac de otrăvire a tabelei cache ARP stocată pe diferite mașini.

Arhitectura containerelor este definită aici, împreună cu schema prin care `middle` îi informează pe `server` și pe `router` cu privire la locația fizică (adresa MAC) unde se găsesc IP-urile celorlalți. 


```
            MIDDLE------------\
        subnet2: 198.7.0.3     \
        MAC: 02:42:c6:0a:00:02  \
               forwarding        \ 
              /                   \
             /                     \
Poison ARP 198.7.0.1 is-at         Poison ARP 198.7.0.2 is-at 
           02:42:c6:0a:00:02         |         02:42:c6:0a:00:02
           /                         |
          /                          |
         /                           |
        /                            |
    SERVER <---------------------> ROUTER <---------------------> CLIENT
net2: 198.7.0.2                      |                           net1: 172.7.0.2
MAC: 02:42:c6:0a:00:03               |                            MAC eth0: 02:42:ac:0a:00:02
                           subnet1:  172.7.0.1
                           MAC eth0: 02:42:ac:0a:00:01
                           subnet2:  198.7.0.1
                           MAC eth1: 02:42:c6:0a:00:01
                           subnet1 <------> subnet2
                                 forwarding
```

Fiecare container execută la secțiunea command în [docker-compose.yml](https://github.com/senisioi/tema5/blob/master/docker-compose.yml) un shell script prin care se configurează rutele. [Cient](https://github.com/senisioi/tema5/blob/master/src/client.sh) și [server](https://github.com/senisioi/tema5/blob/master/src/server.sh) setează ca default gateway pe router (anulând default gateway din docker). În plus, adaugă ca nameserver 8.8.8.8, dacă vreți să testați [DNS spoofing](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/README.md#scapy_dns_spoofing). [Middle](https://github.com/senisioi/tema5/blob/master/src/middle.sh) setează `ip_forwarding=1` și regula: `iptables -t nat -A POSTROUTING -j MASQUERADE` pentru a permite mesajelor care sunt [forwardate de el să iasă din rețeaua locală](https://askubuntu.com/questions/466445/what-is-masquerade-in-the-context-of-iptables). 


Rulati procesul de otrăvire a tabelei ARP din diagrama de mai sus pentru containerele `server` și `router` în mod constant, cu un time.sleep de câteva secunde pentru a nu face flood de pachete. (Hint: puteți folosi două [thread-uri](https://realpython.com/intro-to-python-threading/#starting-a-thread) pentru otrăvirea routerului și a serverului).


Pe lângă print-urile și mesajele de logging din programele voastre, rulați în containerul middle: `tcpdump -SntvXX -i any` iar pe `server` faceți un `wget http://moodle.fmi.unibuc.ro`. Dacă middle este capabil să vadă conținutul HTML din request-ul server-ului, înseamnă că atacul a reușit. Altfel încercați să faceți clean la cache-ul ARP al serverului.


## 2. TCP Hijacking (5%)

Modificați `tcp_server.py` și `tcp_client.py` din repository și rulați-le pe containerul `server`, respectiv `client` ca să-și trimită în continuu unul altuia mesaje random (generați text sau numere, ce vreți voi). Puteți folosi time.sleep de o secundă/două să nu facă flood. Folosiți soluția de la exercițiul anterior pentru a vă interpune în conversația dintre `client` și `server`.
După ce ați reușit atacul cu ARP spoofing și interceptați toate mesajele, modificați conținutul mesajelor trimise de către client și de către server și inserați voi un mesaj adițional în payload-ul de TCP. Dacă atacul a funcționat atât clientul cât și serverul afișează mesajul pe care l-ați inserat. Atacul acesta se numeșete [TCP hijacking](https://www.geeksforgeeks.org/session-hijacking/) pentru că atacatorul devine un [proxy](https://en.wikipedia.org/wiki/Proxy_server) pentru conexiunea TCP dintre client și server.


### Indicații de rezolvare

1. Puteți urmări exemplul din capitolul 3 despre [Netfilter Queue](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/README.md#scapy_nfqueue) pentru a pune mesajele care circulă pe rețeaua voastră într-o coadă ca să le procesați cu scapy.
2. Urmăriți exemplul [DNS Spoofing](https://github.com/senisioi/computer-networks/blob/2020/capitolul3/README.md#scapy_dns_spoofing) pentru a vedea cum puteți altera mesajele care urmează a fi redirecționate într-o coadă și pentru a le modifica payload-ul înainte de a le trimite (adică să modificați payload-ul înainte de a apela packet.accept()).
4. Verificați dacă pachetele trimise/primite au flag-ul PUSH setat. Are sens să alterați SYN sau FIN?
5. Țineți cont de lungimea mesajului pe care îl introduceți pentru ajusta Sequence Number (sau Acknowledgement Number?), dacă e necesar.
6. Încercați întâi să captați și să modificați mesajele de pe containerul router pentru a testa TCP hijacking apoi puteți combina exercițiul 1 cu metoda de hijacking.
7. Scrieți pe [gitter](https://gitter.im/unibuc-computer-networks/2020) orice întrebări aveți, indiferent de cât de simple sau complicate vi se par.
