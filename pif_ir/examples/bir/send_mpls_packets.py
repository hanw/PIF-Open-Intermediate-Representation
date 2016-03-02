#!/usr/bin/env python

import random
from scapy.all import *

class MPLS(Packet):
    name = "MultiProtocol Label Switching"
    fields_desc = [BitField("label", 0x12345, 20),
                   BitField("tc", 0, 3),
                   BitField("s", 1, 1),
                   ByteField("ttl", 0x64)]
bind_layers(Ether, MPLS, type=0x8847)

ipv4 = IP(id=0, flags=0, frag=0, ttl=0, proto=0)
labels = [0xCCCCC, 0xDDDDD, 0xEEEEE, 0xFFFFF]

pkts = []
for _ in range(10):
    pkts.append(Ether() / MPLS(label=random.choice(labels)) / IP())

sendp(pkts, iface='veth1')
