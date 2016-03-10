#!/usr/bin/env python
import logging
import struct

from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.packet_instance import PacketInstance
from pif_ir.bir.utils.bir_parser import BIRParser

from test_common import yaml_eth_struct_dict

def fail(case):
    logging.error("Test Case {}: Failed".format(case))
    exit(1)

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

packet = PacketInstance(pkt, {}, None)
header = BIRStruct('eth', yaml_eth_struct_dict)
parser = BIRParser()

if parser.eval_cond("0x800 == 0x8800", header, packet) != False:    fail(0)
if parser.eval_cond("0x0800 == 0x800", header, packet) != True:     fail(1)
if parser.eval_cond("0 == 0x0", header, packet) != True:            fail(2)
if parser.eval_cond("1 == 0x1", header, packet) != True:            fail(3)
if parser.eval_cond("(10 > 11--)", header, packet) != False:        fail(4)
if parser.eval_cond("10 >= 11--", header, packet) != True:          fail(5)

if parser.eval_inst("(~(0xA + 10) & 0xFF)", header, packet) != 235: fail(6)
if parser.eval_inst("10++ + 11", header, packet) != 22:             fail(7)

if parser.eval_cond("(type_ == 0x0800)", header, packet) != True:   fail(8)
if parser.eval_cond("type_ != 0x0800", header, packet) != False:    fail(9)

if parser.eval_inst("(type_ + 1) & 0xFF00", header, packet) != 0x0800:
    fail(10)
if parser.eval_inst("type_++ & 0xFF00", header, packet) != 0x0800:  fail(11)
