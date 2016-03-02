#!/usr/bin/env python
import logging
import struct
from pif_ir.bir.objects.value_instance import ValueInstance

logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

data = struct.pack("BBBBBBBB", 0x81, 0, 0xa1, 0x64, 0x81, 0, 0, 0xc8)
pkt = bytearray(data)

# test cases: (size, offset, expected result)
tests = [(8, 0, 0x81), (16, 0, 0x8100), (3, 0, 4), (12, 0, 0x810),
         (8, 3, 0x08), (16, 3, 0x0805), (3, 3, 0), (12, 3, 0x080),
         (8, 7, 0x80), (16, 7, 0x8050), (3, 7, 4), (12, 7, 0x805),
         (3, 5, 1), (12, 4, 0x100), (13, 19, 0x164)]

for case, args in enumerate(tests):
    val = ValueInstance('val', args[0])
    val.extract(pkt, bit_offset=args[1])
    if int(val) != args[2]:
        logging.error("Test Case {0}: {1} != {2}".format(
            case, hex(int(val)), hex(args[2])))
        exit(1)

values = range(16)
values.extend([0xaaaaaaaa, 0x55555555, 0xffffffff])

for width in range(1, 33):
    for offset in range(32):
        for value in values:
            test = "{0}_{1}".format(width, offset)
            val = ValueInstance(test, width, value)

            byte_list = bytearray(8)
            for idx in range(8):
                byte_list[idx] = 0xff
            val.update(byte_list, offset)
            val.extract(byte_list, offset)

            expect = value & ((2**width)-1)
            if int(val) != expect:
                msg = "value {0}, width {1}, offset {2}: {3} != {4}".format(
                    value, width, offset, hex(int(val)), hex(expect))
                logging.error(msg)
                exit(1)

# Test with all 0 bits as baseline
for width in range(1,33):
    for offset in range(32):
        for value in values:
            test = "{0}_{1}".format(width, offset)
            val = ValueInstance(test, width, value)

            byte_list = bytearray(8)
            val.update(byte_list, offset)
            val.extract(byte_list, offset)

            expect = value & ((2**width)-1)
            if int(val) != expect:
                msg = "value {0}, width {1}, offset {2}: {3} != {4}".format(
                    value, width, offset, hex(int(val)), hex(expect))
                logging.error(msg)
                exit(1)

