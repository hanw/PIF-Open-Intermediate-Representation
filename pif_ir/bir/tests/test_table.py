#!/usr/bin/env python
import logging 

from pif_ir.bir.objects.bir_struct import BIRStruct
from pif_ir.bir.objects.metadata_instance import MetadataInstance
from pif_ir.bir.objects.table import Table
from pif_ir.bir.objects.table_entry import TableEntryExact

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
table_0.add_entry(TableEntryExact(key_0, val_0))

key_1 = {'type_':0x0800}
val_1 = {'hit':1, 'p4_action':1, 'action_0_arg0':456, 'action_1_arg0':0} 
table_0.add_entry(TableEntryExact(key_1, val_1))

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

