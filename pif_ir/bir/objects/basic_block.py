import logging

from pif_ir.bir.utils.exceptions import BIRControlStateError
from pif_ir.bir.utils.exceptions import BIRRefError
from pif_ir.bir.utils.exceptions import BIRInstructionListError
from pif_ir.bir.utils.validate import check_attributes
from pif_ir.bir.utils.validate import check_basic_block_instructions

class BasicBlock(object):
    """
    @brief Class for a basic block that can be executed within a control flow

    A basic block in BIR carries out a set of instructions, within an optional
    context comprising a header of a packet at some offset and/or a table.
    It then optionally updates the packet offset, and either transitions
    to another basic block or terminates the control flow.
    """
    required_attributes = ['instructions', 'next_control_state']

    def __init__(self, name, bb_attrs, bir_headers, bir_tables, 
                 bir_other_modules, bir_parser):
        check_attributes(name, bb_attrs, BasicBlock.required_attributes)
        logging.debug("Adding basic_block {0}".format(name))

        # set the name
        self.name = name
        self.local_header = None
        self.local_table = None
        self.instructions = []
        self.instructions = bb_attrs['instructions']

        self.next_offset = []   # based on 'next_control_state'
        self.next_state = []    # based on 'next_control_state'
        self._handle_next_control_state(bb_attrs['next_control_state'])

        self.other_modules = bir_other_modules
        self.bir_parser = bir_parser

        # set the local_header
        header_name = bb_attrs.get('local_header', None)
        if header_name:
            if  header_name not in bir_headers.keys():
                raise BIRRefError(header_name, self.name)
            self.local_header = bir_headers[header_name]

        # set the local_table
        table_name = bb_attrs.get('local_table', None)
        if table_name:
            if  table_name not in bir_tables.keys():
                raise BIRRefError(table_name, self.name)
            self.local_table = bir_tables[table_name]


    def _handle_next_control_state(self, ncs_attrs):
        # next_control_state format:
        #   - [cond, offset_expr]       // any number
        #   - offset_expr               // default
        #   - [cond, next_basic_block]  // any number
        #   - next_basic_block          // default
        target = self.next_offset
        for attr in ncs_attrs:
            if not isinstance(attr, list):
                target.append([True, attr])
                target = self.next_state
            else:
                target.append(attr)
        # we need know what the next_offset is, and what state to go to.
        if len(self.next_offset) < 1 or self.next_offset[-1][0] != True:
            raise BIRControlStateError(self.name)
        if len(self.next_state) < 1 or self.next_state[-1][0] != True:
            raise BIRControlStateError(self.name)

    def _assign(self, sink, value, header, packet, bit_offset):
        sink = sink.split('.')
        if len(sink) == 2:
            packet.metadata[sink[0]].set_value(sink[1], value)
        else:
            size = header.field_size(sink[0])
            offset = bit_offset + header.field_offset(sink[0])
            packet.set_bits(value, size, offset) 

    def _get_next_offset(self, packet, bit_offset):
        for cond in self.next_offset:
            if cond[0] == True:
                return self.bir_parser.eval_inst(cond[1], self.local_header,
                                                 packet, bit_offset)

            elif self.bir_parser.eval_cond(cond[0], self.local_header, packet,
                                           bit_offset):
                return self.bir_parser.eval_inst(cond[1], self.local_header,
                                                 packet, bit_offset)
        raise BIRControlStateError(self.name)

    def _get_next_state(self, packet, bit_offset):
        for cond in self.next_state:
            if cond[0] == True:
                return cond[1]
            elif self.bir_parser.eval_cond(cond[0], self.local_header, packet, 
                                           bit_offset):
                return cond[1]

    def _handle_v_call(self, instruction, packet, bit_offset):
        result = self.bir_parser.eval_inst(instruction[2], self.local_header,
                                           packet, bit_offset)
        self._assign(instruction[1], result, self.local_header, packet,
                     bit_offset)

    def _handle_o_call(self, instruction, packet, bit_offset):
        """ Built-in Operations
        """
        op = instruction[1]
        args = instruction[2]

        if op == 'tLookup':
            resp = packet.metadata[args[0]]
            req = packet.metadata[args[1]]
            if self.local_table:
                self.local_table.lookup(req, resp)

        elif op == 'hInsert':
            length = args[0] if len(args) > 0 else len(self.local_header)
            packet.insert(length, bit_offset)
        elif op == 'hRemove':
            length = args[0] if len(args) > 0 else len(self.local_header)
            packet.remove(length, bit_offset)
        elif op == 'tInsert':
            pass    # FIXME: to be implemented
        elif op == 'tRemove':
            pass    # FIXME: to be implemented
        else:
            raise BIRRefError(op, self.name)

    def _handle_m_call(self, instruction, packet, bit_offset):
        op = instruction[1]
        if op not in self.other_modules.keys():
            raise BIRRefError(instruction[1], self.name)
        module = self.other_modules[op]

        if len(instruction[2]) != 2:
            raise BIRInstructionListError(self.name,
                                          "M instructions require 2 arguments")

        # TODO: to ensure correctness, the data_in should be a copy of the 
        #       metadata instance.
        data_out = instruction[2][0]
        if data_out:
            data_out = packet.metadata[data_out]

        data_in = instruction[2][1]
        if data_in:
            data_in = packet.metadata[data_in]

        module(data_in, data_out)

    def process(self, packet, bit_offset=0):
        check_basic_block_instructions(self.name, self.instructions)

        for inst in self.instructions:
            if inst[0] == 'V':
                self._handle_v_call(inst, packet, bit_offset)
            elif inst[0] == 'O':
                self._handle_o_call(inst, packet, bit_offset)
            elif inst[0] == 'M':
                self._handle_m_call(inst, packet, bit_offset)
            else:
                raise BIRInstructionListError(self.name, "unknown instruction")

        next_offset = self._get_next_offset(packet, bit_offset)
        if next_offset < bit_offset:
            raise BIRControlStateError(self.name)

        next_state = self._get_next_state(packet, bit_offset)
        if next_state == "$done$":
            next_state = None
        return next_offset, next_state

