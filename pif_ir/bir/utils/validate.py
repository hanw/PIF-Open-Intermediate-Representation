from pif_ir.bir.utils.exceptions import *

def check_attributes(obj_name, attributes, required_attributes):
    for attr in required_attributes:
        if attr not in attributes:
            raise BIRYamlAttrError(attr, obj_name)

def check_basic_block_instructions(obj_name, instructions):
    # hInsert can only appear as the first instruction
    # hRemove can only appear as the last instruction
    # only one hInsert, or hRemove instruction
    has_h_call = False
    for inst in instructions:
        if inst[0] == 'M' and inst[1] == 'hInsert':
            if inst != instructions[0]:
                raise BIRInstructionListError(obj_name,
                                              "hInsert is not the first call")
            if has_h_call:
                raise BIRInstructionListError(obj_name,
                                              "multiple hInsert/hRemove calls")
            has_h_call = True

        if inst[0] == 'M' and inst[1] == 'hRemove':
            if inst != instructions[-1]:
                raise BIRInstructionListError(obj_name,
                                              "hRemove is not the last call")
            if has_h_call:
                raise BIRInstructionListError(obj_name,
                                              "multiple hInsert/hRemove calls")
            has_h_call = True

