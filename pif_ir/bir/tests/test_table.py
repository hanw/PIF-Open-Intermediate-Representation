#!/usr/bin/env python
import logging 

from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.metadata_instance import MetadataInstance
from pif_ir.bir.objects.table import Table
from pif_ir.bir.objects.table_entry import TableEntry

from test_common import yaml_eth_struct_dict
from test_common import yaml_req_struct_dict
from test_common import yaml_resp_struct_dict
from test_common import yaml_req_meta_dict
from test_common import yaml_resp_meta_dict
from test_common import yaml_table_dict


logging.basicConfig(level=logging.INFO)
logging.info("RUNNING TEST: %s" % __file__)

bir_structs = {
    'eth_t' : BIRStruct('eth_t', yaml_eth_struct_dict),
    'req_t' : BIRStruct('req_t', yaml_req_struct_dict),
    'resp_t' : BIRStruct('resp_t', yaml_resp_struct_dict)
}

table_0 = Table('table_0', yaml_table_dict)

key_0 = {'type_':0x8100}
val_0 = {'hit':1, 'p4_action':2, 'action_0_arg0':0, 'action_1_arg0':123} 
table_0.add_entry(TableEntry('exact', val_0, key_0, None))

key_1 = {'type_':0x0800}
val_1 = {'hit':1, 'p4_action':1, 'action_0_arg0':456, 'action_1_arg0':0} 
table_0.add_entry(TableEntry('exact', val_1, key_1, None))

key_2 = {'type_':0x0800}
msk_2 = {'type_':0xFF00}
val_2 = {'hit':1, 'p4_action':3, 'action_0_arg0':789, 'action_1_arg0':2}
table_0.add_entry(TableEntry('ternary', val_2, key_2, msk_2))

key_3 = MetadataInstance('req_t', yaml_req_meta_dict, bir_structs)
msk_3 = MetadataInstance('req_t', yaml_req_meta_dict, bir_structs)
val_3 = MetadataInstance('resp_t', yaml_resp_meta_dict, bir_structs)
key_3.set_value('type_', 0x9100)
msk_3.set_value('type_', 0xFF00)
val_3.set_value('hit', 1)
val_3.set_value('p4_action', 4)
val_3.set_value('action_0_arg0', 5)
val_3.set_value('action_1_arg0', 4)
table_0.add_entry(val_3, key_3, msk_3)

req_meta = MetadataInstance('req_t', yaml_req_meta_dict, bir_structs)
resp_meta = MetadataInstance('resp_t', yaml_resp_meta_dict, bir_structs)

req_meta.set_value('type_', 0x8100)
table_0.lookup(req_meta, resp_meta)
if (resp_meta.get_value('hit') != 1 or
    resp_meta.get_value('p4_action') != 2 or
    resp_meta.get_value('action_0_arg0') != 0 or
    resp_meta.get_value('action_1_arg0') != 123):
    logging.error("failed test case 1")
    exit(1)

req_meta.set_value('type_', 0x0800)
table_0.lookup(req_meta, resp_meta)
if (resp_meta.get_value('hit') != 1 or
    resp_meta.get_value('p4_action') != 1 or
    resp_meta.get_value('action_0_arg0') != 456 or
    resp_meta.get_value('action_1_arg0') != 0):
    logging.error("failed test case 2")
    exit(1)

req_meta.set_value('type_', 0x0811)
table_0.lookup(req_meta, resp_meta)
if (resp_meta.get_value('hit') != 1 or
    resp_meta.get_value('p4_action') != 3 or
    resp_meta.get_value('action_0_arg0') != 789 or
    resp_meta.get_value('action_1_arg0') != 2):
    logging.error("failed test case 3")
    exit(1)

req_meta.set_value('type_', 0x9123)
table_0.lookup(req_meta, resp_meta)
if (resp_meta.get_value('hit') != 1 or
    resp_meta.get_value('p4_action') != 4 or
    resp_meta.get_value('action_0_arg0') != 5 or
    resp_meta.get_value('action_1_arg0') != 4):
    logging.error("failed test case 4")
    exit(1)

table_0.remove_entry(key_1, None)
table_0.remove_entry(key_3, msk_3)

req_meta.set_value('type_', 0x9123)
resp_meta.reset_values()
table_0.lookup(req_meta, resp_meta)
if resp_meta.get_value('hit') != 0:
    logging.error("failed test case 5")
    exit(1)
