#!/bin/bash

# 50% loos on eth0 and eth1
tc qdisc add dev eth0 root netem loss 70% && \
tc qdisc add dev eth1 root netem loss 85% && \
sleep infinity