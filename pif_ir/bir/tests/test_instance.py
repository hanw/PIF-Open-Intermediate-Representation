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
    yaml_file = os.path.join(local_dir, 'bir_sample.yml')

eth_data = struct.pack("BBBBBB", 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA)
eth_data += struct.pack("BBBBBB", 0xBB, 0xBB, 0xBB, 0xBB, 0xBB, 0xBB)
eth_data += struct.pack("BB", 0x08, 0x00)

ipv4_data = struct.pack("BBBB", 0x40, 0xFF, 0x00, 0x05)
ipv4_data += struct.pack("BBBB", 0x11, 0x11, 0x11, 0x11)
ipv4_data += struct.pack("BBBB", 0xFE, 0x11, 0x00, 0x00)
ipv4_data += struct.pack("BBBB", 0xFF, 0xFF, 0xFF, 0xFF)
ipv4_data += struct.pack("BBBB", 0xEE, 0xEE, 0xEE, 0xEE)

udp_data = struct.pack("BB", 0x22, 0x22)
udp_data += struct.pack("BB", 0x33, 0x33)
udp_data += struct.pack("BB", 0x44, 0x44)
udp_data += struct.pack("BB", 0x55, 0x55)

pkt = bytearray(eth_data + ipv4_data + udp_data)

try:
    instance = BirInstance("instance", yaml_file, transmit_packet)
    instance.process_table_init()
    instance.enable()
    instance.process_packet(1, pkt)
except BIRError as e:
    print e.value
    exit(1)

