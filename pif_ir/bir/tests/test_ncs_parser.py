#!/usr/bin/env python
import logging
import struct

from pif_ir.bir.utils.ncs_parser import NCSParser

logging.basicConfig(level=logging.DEBUG)
logging.info("RUNNING TEST: %s" % __file__)

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

NCS = NCSParser()
if NCS.evaluate("0x800 == 0x8800", None, pkt) != False:
    logging.error("Test Case 0: failed")
    exit(1)

if NCS.evaluate("0x0800 == 0x800", None, pkt) != True:
    logging.error("Test Case 1: failed")
    exit(1)


