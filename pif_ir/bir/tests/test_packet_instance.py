#!/usr/bin/env python
import logging
import struct

from pif_ir.bir.objects.packet_instance import PacketInstance

logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

# packet to extract data from
eth_data = struct.pack("BBBBBB", 0xAA, 0xBB, 0xCC, 0x11, 0x22, 0x33)
eth_data += struct.pack("BBBBBB", 0xff, 0xff, 0xff, 0xff, 0xff, 0xff)
eth_data += struct.pack("BB", 0x81, 0x00)
eth_pkt = bytearray(eth_data)

pkt = PacketInstance(eth_pkt, {}, None)
if pkt.get_bits(8, 96) != 0x81:
    logging.error("failed test case 0")
    exit(1)

if pkt.get_bits(16, 96) != 0x8100:
    logging.error("failed test case 1")
    exit(1)

if pkt.get_bits(7, 95) != 0x60:
    logging.error("failed test case 2")
    exit(1)

pkt.set_bits(0, 7, 95)
if pkt.get_bits(7, 95) != 0x0:
    logging.error("failed test case 3")
    exit(1)

pkt.set_bits(0xFF, 7, 95)
if pkt.get_bits(7, 95) != 0x7F:
    logging.error("failed test case 4")
    exit(1)
