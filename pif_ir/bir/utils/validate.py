from pif_ir.bir.utils.exceptions import *

def check_attributes(obj_name, attributes, required_attributes):
    for attr in required_attributes:
        if attr not in attributes:
            raise BIRYamlAttrError(attr, obj_name)

def check_instructions(obj_name, instructions):
    # hInsert can only appear as the first instruction
    # hRemove can only appear as the last instruction
    # only one hInsert, or hRemove instruction
    has_h_call = False
    for inst in instructions:
        if inst[0] == 'M' and inst[1] == 'hInsert':
            if inst != instructions[0]:
                raise BIRInstructionError(obj_name,
                                          "hInsert is not the first call")
            if has_h_call:
                raise BIRInstructionError(obj_name,
                                          "multiple hInsert/hRemove calls")
            has_h_call = True

        if inst[0] == 'M' and inst[1] == 'hRemove':
            if inst != instructions[-1]:
                raise BIRInstructionError(obj_name,
                                          "hRemove is not the last call")
            if has_h_call:
                raise BIRInstructionError(obj_name,
                                          "multiple hInsert/hRemove calls")
            has_h_call = True

def check_control_state(obj_name, control_state_attributes):
    # has only 2 attributes (i.e. offset, basic_block)
    if len(control_state_attributes) != 2:
        raise BIRControlStateError(obj_name, "expecting 2 attributes")

    # offset conditions format must be [cond, offset]
    # must have a default offset (not required to be the last!)
    default_offset = False
    for cond in control_state_attributes[0]:
        if isinstance(cond, list) and len(cond) == 2:
            pass
        elif isinstance(cond, str) or isinstance(cond, int):
            default_offset = True
        else:
            msg = "unexpected offset condition: {}".format(cond)
            raise BIRControlStateError(obj_name, msg)
    if not default_offset:
        raise BIRControlStateError(obj_name, "missing default offset")

    # basic_block conditions format must be [cond, basic_block]
    # must have a default basic_block (not required to be the last!)
    default_bb = False
    for cond in control_state_attributes[1]:
        if isinstance(cond, list) and len(cond) == 2:
            pass
        elif isinstance(cond, str):
            default_bb = True
        else:
            msg = "unexpected basic_block condition: {}".format(cond)
            raise BIRControlStateError(obj_name, msg)
    if not default_bb:
        raise BIRControlStateError(obj_name, "missing default basic block")
