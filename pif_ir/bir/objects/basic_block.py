import logging

from pif_ir.bir.objects.control_state import ControlState

from pif_ir.bir.utils.exceptions import BIRRefError
from pif_ir.bir.utils.exceptions import BIRInstructionListError
from pif_ir.bir.utils.validate import check_attributes
from pif_ir.bir.utils.validate import check_basic_block_instructions
from pif_ir.bir.utils.validate import check_control_state

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

        self.name = name
        self.local_header = None
        self.local_table = None
        self.other_modules = bir_other_modules
        self.bir_parser = bir_parser

        self.instructions = []
        self.instructions = bb_attrs['instructions']
        check_basic_block_instructions(self.name, self.instructions)

        check_control_state(self.name, bb_attrs['next_control_state'])
        self.control_state = ControlState(bb_attrs['next_control_state'],
                                          self.bir_parser)

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

    def _assign(self, sink, value, header, packet, bit_offset):
        sink = sink.split('.')
        if len(sink) == 2:
            packet.metadata[sink[0]].set_value(sink[1], value)
        else:
            size = header.field_size(sink[0])
            offset = bit_offset + header.field_offset(sink[0])
            packet.set_bits(value, size, offset) 

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
        for inst in self.instructions:
            if inst[0] == 'V':
                self._handle_v_call(inst, packet, bit_offset)
            elif inst[0] == 'O':
                self._handle_o_call(inst, packet, bit_offset)
            elif inst[0] == 'M':
                self._handle_m_call(inst, packet, bit_offset)
            else:
                raise BIRInstructionListError(self.name, "unknown instruction")

        return self.control_state.process(self.local_header, packet, bit_offset)

