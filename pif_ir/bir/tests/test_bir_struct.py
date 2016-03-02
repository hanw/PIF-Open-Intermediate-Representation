#!/usr/bin/env python
import logging
from pif_ir.bir.objects.bir_struct import BIRStruct
from test_common import yaml_eth_struct_dict

logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

bir_struct = BIRStruct('eth_t', yaml_eth_struct_dict)

# Test field_offset() function
offset_tests = [('dst', 0), ('src', 48), ('type_', 96), ('bad', 0)]
for tc, test in enumerate(offset_tests):
    offset = bir_struct.field_offset(test[0])
    if offset != test[1]:
        logging.error("failed offset test case {}: {} != {}".format(
            tc, offset, test[1]))
        exit(1)

# Test field_size() function
size_tests = [('dst', 48), ('src', 48), ('type_', 16), ('bad', 0)]
for tc, test in enumerate(size_tests):
    offset = bir_struct.field_size(test[0])
    if offset != test[1]:
        logging.error("failed size test case {}: {} != {}".format(
            tc, offset, test[1]))
        exit(1)

