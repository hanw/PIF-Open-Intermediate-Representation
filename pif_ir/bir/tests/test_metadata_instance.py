#!/usr/bin/env python
import logging
import struct
from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.metadata_instance import MetadataInstance
from test_common import yaml_eth_struct_dict
from test_common import yaml_eth_meta_dict

logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

# packet to extract data from
eth_data = struct.pack("BBBBBB", 0xAA, 0xBB, 0xCC, 0x11, 0x22, 0x33)
eth_data += struct.pack("BBBBBB", 0xff, 0xff, 0xff, 0xff, 0xff, 0xff)
eth_data += struct.pack("BB", 0x81, 0x00)
eth_pkt = bytearray(eth_data)

# bir structs for the the metadata fields
bir_structs = {'eth_t':BIRStruct('eth_t', yaml_eth_struct_dict)}

metadata = MetadataInstance('eth', yaml_eth_meta_dict, bir_structs, 
                            buf=eth_pkt)
if len(metadata) != 112:
    logging.error("failed len(metadata): {} != 112".format(len(metadata)))
    exit(1)

if metadata.get_value('type_') != 0x8100:
    logging.error("failed get_value() call")
    exit(1)

metadata.set_value("type_", 0xFFFF)
if metadata.get_value('type_') != 0xffff:
    logging.error("failed set_value() call")
    exit(1)

