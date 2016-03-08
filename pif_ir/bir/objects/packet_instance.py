import logging

from pif_ir.bir.objects.metadata_instance import MetadataInstance
from pif_ir.bir.utils.common import int_to_bytearray, bytearray_to_int
from pif_ir.bir.utils.exceptions import *

class PacketInstance(object):
    id_next = 0

    def __init__(self, packet_data, metadata_attrs, bir_structs):
        """
        @brief PacketInstance constructor
        @param packet_data The original packet data as a byte array
        @param metadata_dict The metadata values associated with the packet
        @param bir_structs The structs used for metadata fields
        """
        self.packet_data = packet_data
        self.idx = PacketInstance.id_next
        PacketInstance.id_next += 1

        self.metadata = {}
        for name, md in metadata_attrs.items():
            self.metadata[name] = MetadataInstance(name, md, bir_structs)
        logging.debug("Created packet %d", self.idx)

    def get_bits(self, bit_width, bit_offset=0):
        return bytearray_to_int(self.packet_data, bit_width, bit_offset)

    def set_bits(self, value, bit_width, bit_offset=0):
        byte_offset = bit_offset / 8 
        offset = bit_offset % 8

        vals, masks = int_to_bytearray(offset, value, bit_width)
        for idx, (val, mask) in enumerate(zip(vals,masks)):
            self.packet_data[byte_offset + idx] &= mask
            self.packet_data[byte_offset + idx] += val

    def insert(self, length, bit_offset=0):
        byte_offset = bit_offset / 8
        offset = bit_offset % 8

        # FIXME: enforced for simplicity
        if offset != 0:
            raise BIRError("packet insert offset should be byte address") 
        if length %8 != 0:
            raise BIRError("packet insert length should be a factor of 8")

        tmp = self.packet_data[:byte_offset]
        tmp += bytearray(length/8)
        tmp += self.packet_data[byte_offset:]
        self.packet_data = tmp

    def remove(self, length, bit_offset=0):
        byte_offset = bit_offset / 8
        offset = bit_offset % 8

        # FIXME: enforced for simplicity
        if offset != 0:
            raise BIRError("packet remove offset should be byte address") 
        if length %8 != 0:
            raise BIRError("packet remove length should be a factor of 8")

        tmp = self.packet_data[:byte_offset]
        tmp += self.packet_data[byte_offset + (length/8):]
        self.packet_data = tmp

