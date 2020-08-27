# Soluție

## 1. Traceroute

Am implementat soluția iar aici este output-ul:

### Ruta către 14.199.255.165
```
1)89.34.210.62-Horezu-Valcea-RO
2)46.102.39.1-Roata de Jos-Giurgiu-RO
3)188.241.237.225-Valeni-Dambovita-Dambovita-RO
4)92.114.118.25-Iasi-Iasi-RO
5)80.81.195.165-Cologne-North Rhine-Westphalia-DE
6)61.244.225.62-Kwai Chung-Tsuen Wan District-HK
7)14.199.255.165-Central-Central and Western District-HK
```

### Ruta către 41.48.253.69
```
1)89.34.210.62-Horezu-Valcea-RO
2)46.102.39.1-Roata de Jos-Giurgiu-RO
3)188.241.237.225-Valeni-Dambovita-Dambovita-RO
4)92.114.118.25-Iasi-Iasi-RO
5)80.81.193.237-Cologne-North Rhine-Westphalia-DE
6)105.16.9.21-Port Louis-Port Louis-MU
7)105.16.13.149-Port Louis-Port Louis-MU
8)105.16.9.213-Port Louis-Port Louis-MU
9)105.16.8.209-Port Louis-Port Louis-MU
10)105.16.29.9-Johannesburg-Gauteng-ZA
11)105.22.32.150-Johannesburg-Gauteng-ZA
12)41.48.253.69-Pretoria-Gauteng-ZA
```

### Ruta către 103.26.68.26
```
1)89.34.210.62-Horezu-Valcea-RO
2)46.102.39.1-Roata de Jos-Giurgiu-RO
3)188.241.237.225-Valeni-Dambovita-Dambovita-RO
4)89.47.220.1-Bucharest-Bucuresti-RO
5)80.97.248.63-Cluj-Napoca-Cluj-RO
6)184.105.65.45-Hartford-Connecticut-US
7)184.105.213.249-Omaha-Nebraska-US
8)184.105.65.58-Hartford-Connecticut-US
9)184.105.80.14-San Francisco-California-US
10)184.105.65.13-Hartford-Connecticut-US
11)184.104.194.138-Manchester-England-GB
12)184.104.194.141-Manchester-England-GB
13)184.104.194.145-Manchester-England-GB
14)103.26.68.26-Canberra-Australian Capital Territory-AU
```


## 2. Reliable UDP

### Emițător - mesaje de logging
Rulăm `docker-compose logs emitator` și punem rezultatul aici:
```
....
....
....
....
....
```


### Receptor - mesaje de logging
Rulăm `docker-compose logs receptor` și punem rezultatul aici:
```
....
....
....
....
....
```
