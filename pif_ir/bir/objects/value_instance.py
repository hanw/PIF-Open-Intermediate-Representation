import logging

from pif_ir.bir.objects import bir_common

class ValueInstance(object):
    def __init__(self, name, bit_width, value=0):
        if bit_width <= 0:
            raise BIRFieldWidthError(name, bit_width)
        logging.debug("Adding value {0}".format(name))
        self.name = name
        self.bit_width = bit_width  
        self.value = value 

    def __len__(self):
        return self.bit_width

    def __int__(self):
        return self.value

    def extract(self, buf, bit_offset=0):
        self.value = bir_common._to_int(buf, self.bit_width, bit_offset)
        return self.value

    def update(self, buf, bit_offset=0):
        byte_offset = bit_offset / 8 
        offset = bit_offset % 8

        vals, masks = bir_common._to_bytearray(offset, self.value, 
                                               self.bit_width)
        for idx, (val, mask) in enumerate(zip(vals,masks)):
            buf[byte_offset + idx] &= mask
            buf[byte_offset + idx] += val

