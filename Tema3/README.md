# Tema 3 

## Informații temă
**Deadline**: **24 aprilie 2020** 

Predarea soluției se va face într-un repository de github în două feluri: 1) adăugați sursele modificate sau folosite în directorul `src`; 2) modificați template-ul [Rezolvare.md](https://github.com/senisioi/tema3/blob/master/Rezolvare.md) și completați raportul cu cerințele de acolo.

Pentru a vă înscrie folosiți acest link: [https://classroom.github.com/g/s0wLIpwC](https://classroom.github.com/g/s0wLIpwC)
Până pe **10 Aprilie** trebuie să formați echipele iar deadline-ul este în săptămâna de după vacanță.

Tema se va rezolva în echipe de maxim două persoane iar punctajul temei este 10% din nota finală de laborator.
Veți fi evaluați individual în funcție de commit-uri în repository prin `git blame` și `git-quick-stats -a`. Doar utilizatorii care apar cu modificări în repository vor fi punctați (în funcție de modificările pe care le fac).


### Barem
1. **Traceroute** - 25%
2. **Reliable UDP** - 75%
    - testarea este obligatorie folosind containerele emitator si receptor
    - obligatoriu să transferați un fișier de cel puțin 100 KB, ex: `/elocal/capitolul3/layers.jpg` de la emițător la receptor
    - obligatoriu să verificați că fișierul trimis a ajuns integru; puteți face acest lucru salvându-l tot în `/elocal` și comparându-l cu cel trimis inițial
    - 25% implementare calcul checksum si verificare la destinație
    - 25% fie implementati [Stop and Wait](https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html) cu window egal 0 sau 1
    - 50% fie implementati [sliding window](http://www.ccs-labs.org/teaching/rn/animations/gbn_sr/) go-back-n sau selective repeat, cu window random între 1 și 5


## Cerințe temă 

### 1. Traceroute

Traceroute este o metodă prin care putem urmări prin ce noduri (routere) trece un pachet pentru a ajunge la destinație.
În funcție de IP-urile acestor noduri, putem afla țările sau regiunile prin care trec pachetele.
Înainte de a implementa tema, citiți explicația felului în care funcționează [traceroute prin UDP](https://www.slashroot.in/how-does-traceroute-work-and-examples-using-traceroute-command). Pe scurt, pentru fiecare mesaj UDP care este în tranzit către destinație, dar pentru care TTL (Time to Live) expiră, senderul primește de la router un mesaj [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Header) de tipul [Time Exceeded TTL expired in transit](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Time_exceeded).

Modificați fișierul [tema3/src/traceroute.py](https://github.com/senisioi/tema3/blob/master/src/traceroute.py) pentru a afișa pentru 3 IP-uri diferite: Orașul, Regiunea și Țara (care sunt disponibile) prin care trece mesajul vostru pentru a ajunge la destinație. Folosiți IP-uri din Asia, Africa și Australia căutând site-uri cu extensia .cn, .za, .au. Folositi IP-urile acestora.


### 2. Reliable UDP
Pentru a transmite date în mod sigur (reliable), avem nevoie de implementarea unor mecanisme de confirmare a datelor transmise. Putem folosi principiul [Stop and Wait](https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html) - se așteaptă o confirmare după fiecare mesaj trimis, dar asta ar însemna că rețeaua nu este folosită în timp ce un emițător așteaptă confirmarea.  Cealaltă opțiune este să trimite o secvență de pachete unul după altul folosind un principiu de [Fereastră Glisantă / Sliding Window](http://www.ccs-labs.org/teaching/rn/animations/gbn_sr/), caz în care putem aștepta confirmări pentru mai multe pachete simultan. 

Protocolul TCP implementează un mecanism de fereastră glisantă, dar prin 3-way handshake, metodele de congestion control, cele de flow control și opțiunile sale, nu oferă neapărat o metodă de transmitere rapidă a datelor, ci una prin care datele sunt transmise în mod sigur (reliable). Scopul acestui exercițiu este să implementați un protocol de transport care să ofere garanția trimiterii mesajului de la un emițător la un receptor folosind UDP și în același timp să obțineți un mecanism prin care datele pot fi transmise mai rapid decât prin TCP într-un mod sigur. Mesajele sunt trasmise unilateral dinspre un emițător spre un receptor. Un astfel de protocol ar putea fi folosit, spre exemplu, pentru file sharing (ex. torrent) sau live streaming.

Aveți deja câteva bucăți de cod care vă pot ajuta în [tema3/src/emitator.py](https://github.com/senisioi/tema3/blob/master/src/emitator.py) și [tema3/src/receptor.py](https://github.com/senisioi/tema3/blob/master/src/receptor.py). Va trebui în primă fază să implementați secțiunile unde scrie TODO apoi celelalte specificații ale protocolului.

Receptorul trimite următoarele informații emițătorului:

- confirmare pentru primirea secvențelor de octeți
- informații cu privire la cât spațiu mai are în buffer pentru primirea de noi date

Emițătorul trimite 3 tipuri de mesaje:

1. cerere de connectare
2. mesaj cu date
3. cerere de finalizare

Pentru a testa protocolul rulați în folosind docker programele emitator si receptor:
```bash

# pentru a da docker-compose up -d este important să ne aflăm 
# în tema3
cd repository-cu-tema-3
docker-compose up -d

# pornim receptorul
docker-compose exec emitator bash -c "python3 /elocal/tema3/src/receptor.py -p 10000 -f $fisier_de_scris"

# pornim emitatorul
docker-compose exec receptor bash -c "python3 /elocal/tema3/src/emitator.py -a $IP_receptor -p 10000 -f $fisier"

# vedem ce printeaza fiecare container
docker-compose logs emitator
docker-compose logs receptor
```

Trebuie să aveți în vedere următoarele aspecte:

- emițătorul trimite mesaje către receptor și folosește implicit containerul router
- containerul router elimină pachete pe eth0 cu probabilitate 70% și pe eth1 cu 85%
- există riscul ca un mesaj să nu ajungă la receptor
- există riscul ca o confirmre să nu ajungă la emițător, atunci emițătorul care apelează  `recvfrom`, în așteptarea unei confirmări, ar trebui să seteze timeout prin `sock.settimeout`
- există riscul ca dintr-o fereastră de 4 trimiteri (`sendto`) să se piardă un mesaj intermediar; în acest caz fie reluați transmisia întregii ferestre, fie retransmiteți doar acele segmente care s-au pierdut
- există riscul ca pachetul să fie alterat pe parcurs

### Specificația Reliable UDP

Vom construi două anteturi noi, unul pentru emițător și unul pentru receptor și vom folosi folosi librăria struct pentru a adăgua în cadrul unui mesaj UDP câteva câmpuri noi.

#### Header mesaj de la emițător:
```
  0               1               2               3              4
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |          Source Port          |       Destination Port        |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-   UDP header
 |          Length               |          Checksum             |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                        Sequence Number                        |  
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-  Header Reliable UDP emițător
 |          Checksum             |S P F|      zeros              |    8 bytes
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                       payload/data                            |  mesaj maxim 1400 de bytes
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
```

Ex. struct:
```python
seq_nr = 11
checksum = 0
spf = 0b100 # seteaza flag S = 1
spf_zero = spf << 13 # muta cei trei biti cu 13 pozitii la stanga
mesaj = b'salut'
header = struct.pack('!LHH', seq_nr, checksum, spf_zero)
de_trimis = header + mesaj
sock.sendto(de_trimis, receptor)
```

##### Sequence Number
Este un număr pe 4 octeți (unsigned long integer, cod '!L'). Un emițător care dorește să trimită receptorului mesaje va incrementa acest număr în funcție de câți octeți sunt trimiși. Numărul de secvență inițial va fi ales aleatoriu între 0 și cel mai mare număr unsigned pe 32 de biți: [4,294,967,295](https://en.wikipedia.org/wiki/4,294,967,295). 
Ex:
```python
# numar de secventa initial
MAX_UINT32 = 0xFFFFFFFF
initial_sequence_nr = random.randint(0, MAX_UINT32)

# daca numarul de secventa curent ar fi:
sequence_nr_curent = 100000
# mesajul/payload ar fi
mesaj = b"salut"
# cand trimitem acest mesaj, trebuie sa setam numarul de secventa:
sequence_nr_curent = sequence_nr_curent + len(mesaj)

# daca mesajul a ajuns cu succes
# receptorul va trimite un mesaj cu Acknowledgment Number == sequence_nr_curent

# Atentie! in cazul in care numarul de secventa + numarul de octeti
# depaseste numarul maxim struct.pack va da eroare
>>> struct.pack('!L', 0xFFFFFFFF + 1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
struct.error: 'L' format requires 0 <= number <= 4294967295
```


##### Checksum
Este un număr pe 2 octeți (unsigned short integer, cod '!H') care se calculează în felul următor:

1. se seteaza checksum inițial cu 0
2. se construiește o variabilă `octeti` care conține antetul și datele care urmează a fi trimise 
3. în cazul în care lungimea `len(octeti)` este impară se mai adaugă un octet de 0 la sfârșit
2. se împarte mesajul (incluzând antetul și datele) în bucăți de câte 2 octeți
4. se adună bucățile de câte 2 octeți într-o sumă pe 16 biți 
5. checksum va fi egal cu complementul sumei; aveți un exemplu de calcul a unui checksum fictiv pe 3 biți [aici](https://github.com/senisioi/computer-networks/tree/2020/capitolul3#checksum)

Valoarea obținută anterior este aduăgată în antetul segmentului înainte de a fi trimis.
Când mesajul este receptat, se refac toți pașii începând cu pasul 3. În urma complementării rezultatul ar trebui să fie 0.

În cazul în care mesajul trimis ajunge la destinație iar checksum nu este 0, atunci mesajul este ignorat (emițătorul ignoră confirmarea iar receptorul ignoră segmentul).

##### Flags
**S** - atunci când emițătorul inițializează o conexiune, trimite un sequence number aleatoriu și marchează primul bit cu 1
**P** - atunci când emițătorul trimite un mesaj cu date, marchează al doilea bit cu 1
**F** - atunci când emițătorul îl informează pe receptor că s-a încheiat transmisia, trimite un mesaj cu al treilea bit setat 1 
**zeros** - 13 zerori pentru padding pana la finalul randului de 32 de biți 

##### Payload / Data
Octeții care vor fi trimiși ca mesaj de la emițător la receptor, maxim 1400 de octeți.

#### Header mesaj de la receptor:
```
  0               1               2               3              4
  0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |          Source Port          |       Destination Port        |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-   UDP header
 |          Length               |          Checksum             |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------
 |                    Acknowledgment Number                      |
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-  Header Reliable UDP receptor
 |             Checksum          |          Window               |    8 bytes
 -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- -----------------

```
Mesajul de la receptor doar confirmă primirea, nu are payload.

##### Acknowledgment Number
Este un număr pe 4 octeți (unsigned long integer, cod '!L'). 
Când receptorul primște un mesaj de tip `S` sau `F`, se returnează ca acknowledgement number valoare sequence number + 1.
Când receptorul primește un segment de tip `P`, se returnează ca acknowledgement number valoarea acelui sequence number reprezentând capătul intervalului.
Ex.:
```python
date, emitator = sock.recvfrom(1400)
header = date[:8]
mesaj = date[8:]
seq_nr, checksum, spf_zero = struct.unpack('!LHH', header)
# eliminam cele 13 zerouri
spf = spf_zero >> 13
if spf & 0b100 or spf & 0b001:
    # inseamna ca am primit S sau F
    ack_nr = seq_nr + 1
elif spf & 0b010:
    # inseamna ca am primit P
    ack_nr = seq_nr
checksum = 0
window = random.randint(1, 5)

octeti = struct.pack('!LHH', ack_nr, checksum, window)
sock.sendto(emitator, octeti)
```
##### Checksum
Un număr pe 2 octeți (unsigned short integer, cod '!H') care este verificat la primire.

##### Window
Un număr pe 2 octeți (unsigned short integer, cod 'H') prin care îl informează pe emițător câte segmente mai poate primi.
Dacă emițătorul primește window = 2, înseamnă că emițătorul ar trebui să execute doar două apeluri `sock.sendto()` cu date de 1400 octeți. Dacă window = 0, emițătorul trebuie să înceteze expedierea segementelor. Dacă valoarea este 1, protcolul va funcționa pe principiul [Stop and Wait](https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html) - se așteaptă o confirmare după fiecare mesaj trimis. Setați ca default `window = random.randint(1, 5)`.
În cazul de față window are altă semnificație [decât la TCP](http://www.inacon.de/ph/data/TCP/Header_fields/TCP-Header-Field-Window-Size_OS_RFC-793.htm), cuantificând numărul de segmente în loc de octeți.

