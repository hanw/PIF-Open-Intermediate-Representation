# single BIRStruct description
yaml_eth_struct_dict = {
    'type' : 'struct',
    'fields' : [ 
        {'dst' : 48},
        {'src' : 48},
        {'type_' : 16} 
    ]
}

yaml_udp_struct_dict = {
    'type' : 'struct',
    'fields' : [
        {'sport' : 16},
        {'dport' : 16},
        {'len' : 16},
        {'chksum' : 16}
    ]
}

yaml_req_struct_dict = {
    'type' : 'struct',
    'fields' : [
        {'type_' : 16}
    ]
}

yaml_resp_struct_dict = {
    'type' : 'struct',
    'fields' : [
        {'hit' : 1},
        {'p4_action' : 2},
        {'action_0_arg0' : 16},
        {'action_1_arg0' : 16} 
    ]
}

# single MetadataInstance description
yaml_eth_meta_dict = {
    'type' : 'metadata',
    'values' : 'eth_t',
    'visibility' : 'inout'
}
yaml_req_meta_dict = {
    'type' : 'metadata',
    'values' : 'req_t',
    'visibility' : 'inout'
}
yaml_resp_meta_dict = {
    'type' : 'metadata',
    'values' : 'resp_t',
    'visibility' : 'inout'
}

# single Table description
yaml_table_dict = {
    'type' : 'table',
    'match_type' : 'ternary',
    'depth' : 64,
    'request' : 'req_t',
    'response' : 'resp_t',
    'operations' : None
}

