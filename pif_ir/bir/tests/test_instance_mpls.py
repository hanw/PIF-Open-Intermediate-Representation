#!/usr/bin/env python
import logging
import os
import struct
import sys

from pif_ir.bir.instance import BirInstance
from pif_ir.bir.utils.exceptions import BIRError

logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

def transmit_packet(out_port, packet):
    pass

if len(sys.argv) > 1:
    yaml_file = sys.argv[1]
else:
    local_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_file = os.path.join(local_dir, 'bir_mpls.yml')

eth_data = struct.pack("BBBBBB", 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
eth_data += struct.pack("BBBBBB", 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
eth_data += struct.pack("BB", 0x88, 0x47)

mpls0_data = struct.pack("BBBB", 0xDD, 0xDD, 0xD0, 0x00)
mpls1_data = struct.pack("BBBB", 0xEE, 0xEE, 0xE0, 0x00)

ipv4_data = struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)
ipv4_data += struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)
ipv4_data += struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)
ipv4_data += struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)
ipv4_data += struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)

udp_data = struct.pack("BB", 0x00, 0x00)
udp_data += struct.pack("BB", 0x00, 0x00)
udp_data += struct.pack("BB", 0x00, 0x00)
udp_data += struct.pack("BB", 0x00, 0x00)

pkt0 = bytearray(eth_data + mpls0_data + ipv4_data + udp_data)
pkt1 = bytearray(eth_data + mpls1_data + ipv4_data + udp_data)

try:
    instance = BirInstance("instance", yaml_file, transmit_packet)
    instance.process_table_init()
    instance.enable()
    instance.process_packet(1, pkt0)
    instance.process_packet(1, pkt1)
except BIRError as e:
    print e.value
    exit(1)

